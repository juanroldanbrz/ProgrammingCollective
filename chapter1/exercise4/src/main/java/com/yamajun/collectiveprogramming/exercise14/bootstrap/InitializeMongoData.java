package com.yamajun.collectiveprogramming.exercise14.bootstrap;

import static java.util.stream.Collectors.toList;

import java.io.IOException;
import java.io.InputStream;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.mongobee.changeset.ChangeLog;
import com.github.mongobee.changeset.ChangeSet;
import com.yamajun.collectiveprogramming.exercise14.model.entity.Movie;
import com.yamajun.collectiveprogramming.exercise14.model.entity.Rating;
import com.yamajun.collectiveprogramming.exercise14.model.processing.UserABSimilarity;
import com.yamajun.collectiveprogramming.exercise14.model.processing.UserRecommendations;

import io.vavr.Tuple;
import io.vavr.Tuple2;
import lombok.extern.slf4j.Slf4j;

@ChangeLog(order = "001")
@Slf4j
public class InitializeMongoData {
    
    private static final String MOVIES_JSON = "json/movies.json";
    private static final String RATINGS_JSON = "json/ratings.json";
    
    @ChangeSet(order = "001", id = "populateMovies", author = "Juan Bermudez")
    public void populateMovies(MongoTemplate mongoTemplate) throws IOException, URISyntaxException {
        ClassLoader classloader = Thread.currentThread().getContextClassLoader();
        InputStream jsonResourceInputStream = classloader.getResourceAsStream(MOVIES_JSON);
        
        ObjectMapper mapper = new ObjectMapper();
        
        List<Movie> moviesList = mapper.readValue(jsonResourceInputStream, new TypeReference<List<Movie>>() {
        });
        
        mongoTemplate.insertAll(moviesList);
    }
    
    @ChangeSet(order = "002", id = "populateRatings", author = "Juan Bermudez")
    public void populateRatings(MongoTemplate mongoTemplate) throws IOException, URISyntaxException {
        
        ClassLoader classloader = Thread.currentThread().getContextClassLoader();
        InputStream jsonResourceInputStream = classloader.getResourceAsStream(RATINGS_JSON);
        
        ObjectMapper mapper = new ObjectMapper();
        
        List<Rating> ratingList = mapper.readValue(jsonResourceInputStream, new TypeReference<List<Rating>>() {
        });
        
        mongoTemplate.insertAll(ratingList);
    }
    
    @ChangeSet(order = "003", id = "calculateUserToUserIdRatings", author = "Juan Bermudez")
    public void precompute(MongoTemplate mongoTemplate) throws IOException, URISyntaxException, InterruptedException {
        
        log.info("Starting precomputing");
        
        final List<Rating> ratingList = mongoTemplate.findAll(Rating.class);
        final Set<String> userIdSet = ratingList.stream().map(Rating::getUserId).collect(Collectors.toSet());
        
        Set<UserABSimilarity> similarityToUserIds = ConcurrentHashMap.newKeySet();
        
        for (String userId : userIdSet) {
            List<Rating> moviesRatedByUser = ratingList.parallelStream().filter(rating -> rating.getUserId().equals(userId))
                    .collect(toList());
            
            userIdSet.parallelStream().forEach(otherUserId -> {
                UserABSimilarity userABSimilarity = new UserABSimilarity(userId, otherUserId, 0d);
                if (userId.equals(otherUserId)) {
                    return;
                }
                
                List<Rating> moviesRatedByUserToCompare = ratingList.parallelStream()
                        .filter(rating -> rating.getUserId().equals(otherUserId)).collect(toList());
                Double similarityResult = calculateEuclideanSim(moviesRatedByUser, moviesRatedByUserToCompare);
                if (similarityResult > 0) {
                    userABSimilarity.setSimilarity(similarityResult);
                    similarityToUserIds.add(userABSimilarity);
                }
            });
        }
        
        log.info("Calculated {} similarities", similarityToUserIds.size());
        
        mongoTemplate.insertAll(similarityToUserIds);
        log.info("Saved to mongoDB");
        log.info("Precomputing finished");
    }
    
    @ChangeSet(order = "005", id = "createRecommendations", author = "Juan Bermudez", runAlways = true)
    public void createRecommendations(MongoTemplate mongoTemplate) {
        final List<String> userIdSet = findListOfUserId(mongoTemplate);
        
        for (String userId : userIdSet) {
            
            List<String> moviesSeenByUserA = findMoviesIdSeenByUserId(userId, mongoTemplate).parallelStream().map(Rating::getMovieId)
                    .collect(toList());
            Query query = new Query();
            query.addCriteria(Criteria.where("userIdA").is(userId)).with(new Sort(Sort.Direction.DESC, "similarity")).limit(5);
            List<UserABSimilarity> userABSimilarities = mongoTemplate.find(query, UserABSimilarity.class);
            
            List<UserRecommendations> userRecommendations = getMoviesRecommendedForUser(userId, moviesSeenByUserA, userABSimilarities,
                    mongoTemplate);
            log.info("Inserting {} recommendations for userId {}", userRecommendations.size(), userId);
            mongoTemplate.insertAll(userRecommendations);
        }
        
    }
    
    private List<String> findListOfUserId(MongoTemplate mongoTemplate) {
        return mongoTemplate.getCollection("rating").distinct("userId");
    }
    
    private List<UserRecommendations> getMoviesRecommendedForUser(String userA, List<String> moviesSeenByUserA,
            List<UserABSimilarity> userABSimilarities, MongoTemplate mongoTemplate) {
        
        Map<String, Tuple2<Double, Double>> movieIdToWeightAndTotal = new ConcurrentHashMap<>();
        userABSimilarities.parallelStream().forEach(userABSimilarity -> {
            List<Rating> moviesWhichUserBRatedAndNotUserA = findMoviesIdSeenByUserId(userABSimilarity.getUserIdB(), mongoTemplate).stream()
                    .filter(rating -> !moviesSeenByUserA.contains(rating.getMovieId())).collect(toList());
            
            moviesWhichUserBRatedAndNotUserA.forEach(rating -> {
                if (!movieIdToWeightAndTotal.containsKey(rating.getMovieId())) {
                    movieIdToWeightAndTotal.put(rating.getMovieId(), Tuple.of(0d, 0d));
                }
                Tuple2<Double, Double> tuple = movieIdToWeightAndTotal.get(rating.getMovieId());
                Double weight = tuple._1 + rating.getRating() * userABSimilarity.getSimilarity();
                Double total = tuple._2 + userABSimilarity.getSimilarity();
                movieIdToWeightAndTotal.put(rating.getMovieId(), Tuple.of(weight, total));
            });
        });
        
        List<UserRecommendations> recommendationsForUser = new ArrayList<>();
        movieIdToWeightAndTotal.forEach((movieId, tuple) -> {
            if (tuple._1() != 0 && tuple._2 != 0) {
                Query query = new Query();
                query.addCriteria(Criteria.where("_id").is(movieId));
                Movie movie = mongoTemplate.findOne(query, Movie.class);
                
                UserRecommendations userRecommendations = new UserRecommendations(userA, movieId, movie.getTitle(), tuple._2 / tuple._1);
                recommendationsForUser.add(userRecommendations);
            }
        });
        
        return recommendationsForUser;
    }
    
    private List<Rating> findMoviesIdSeenByUserId(String userId, MongoTemplate mongoTemplate) {
        Query query = new Query();
        query.addCriteria(Criteria.where("userId").is(userId));
        return mongoTemplate.find(query, Rating.class);
        
    }
    
    private Double calculateEuclideanSim(List<Rating> source, List<Rating> target) {
        Double sumOfSquares = 0d;
        int matches = 0;
        Map<String, Float> targetIdToRatingMap = target.parallelStream().filter(source::contains)
                .collect(Collectors.toMap(Rating::getMovieId, Rating::getRating));
        
        for (Rating sourceRating : source) {
            if (targetIdToRatingMap.containsKey(sourceRating.getMovieId())) {
                Float targetMovieOtherUserRating = targetIdToRatingMap.get(sourceRating.getMovieId());
                Float targetMovieMeRating = sourceRating.getRating();
                matches++;
                sumOfSquares += Math.pow(targetMovieMeRating - targetMovieOtherUserRating, 2);
            }
        }
        
        if (sumOfSquares == 0) {
            return 0d;
        }
        
        return (1 / (1 + sumOfSquares)) / ((source.size() + 1) / matches);
    }
    
}
