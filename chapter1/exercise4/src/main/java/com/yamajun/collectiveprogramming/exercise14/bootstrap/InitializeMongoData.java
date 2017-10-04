package com.yamajun.collectiveprogramming.exercise14.bootstrap;

import java.io.IOException;
import java.io.InputStream;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

import org.springframework.data.mongodb.core.MongoTemplate;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.mongobee.changeset.ChangeLog;
import com.github.mongobee.changeset.ChangeSet;
import com.yamajun.collectiveprogramming.exercise14.model.entity.Movie;
import com.yamajun.collectiveprogramming.exercise14.model.entity.Rating;
import com.yamajun.collectiveprogramming.exercise14.model.processing.SimilarityToUserId;

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
    public void precompute(MongoTemplate mongoTemplate) throws IOException, URISyntaxException {

        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Rating> ratingList = mongoTemplate.findAll(Rating.class);
        Set<String> userIdSet = ratingList.stream().map(Rating::getUserId).collect(Collectors.toSet());
        
        List<SimilarityToUserId> similarityToUserIds = new ArrayList<>();
        
        for (String userId : userIdSet) {
            List<Rating> moviesRatedByUser = ratingList.parallelStream().filter(rating -> rating.getUserId().equals(userId))
                    .collect(Collectors.toList());
            SimilarityToUserId userToUserSimilarity = new SimilarityToUserId();
            userToUserSimilarity.setUserId(userId);
            userToUserSimilarity.setSimilarityToUserId(new TreeMap<>(Comparator.reverseOrder()));


            for (String otherUserId : userIdSet) {
                //@TODO Improve this
                if (userId.equals(otherUserId)) {
                    continue;
                }
                List<Rating> moviesRatedByUserToCompare = ratingList.parallelStream()
                        .filter(rating -> rating.getUserId().equals(otherUserId)).collect(Collectors.toList());
                Double similarityResult = calculateEuclideanSim(moviesRatedByUser, moviesRatedByUserToCompare);
                if (similarityResult > 0) {
                    userToUserSimilarity.getSimilarityToUserId().put(similarityResult, otherUserId);
                }

            }

            similarityToUserIds.add(userToUserSimilarity);
        }
        
        mongoTemplate.insertAll(similarityToUserIds);
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
