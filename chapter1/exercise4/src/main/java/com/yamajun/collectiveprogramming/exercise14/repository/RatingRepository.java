package com.yamajun.collectiveprogramming.exercise14.repository;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.yamajun.collectiveprogramming.exercise14.model.entity.Movie;
import com.yamajun.collectiveprogramming.exercise14.model.entity.Rating;

public interface RatingRepository extends MongoRepository<Rating, String>{

}
