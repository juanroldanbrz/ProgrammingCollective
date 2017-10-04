package com.yamajun.collectiveprogramming.exercise14.repository;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.yamajun.collectiveprogramming.exercise14.model.entity.Movie;

public interface MovieRepository extends MongoRepository<Movie, String>{

}
