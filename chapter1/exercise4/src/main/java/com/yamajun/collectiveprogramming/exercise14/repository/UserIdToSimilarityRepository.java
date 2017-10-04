package com.yamajun.collectiveprogramming.exercise14.repository;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.yamajun.collectiveprogramming.exercise14.model.processing.SimilarityToUserId;

public interface UserIdToSimilarityRepository extends MongoRepository<SimilarityToUserId, String>{

}
