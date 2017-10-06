package com.yamajun.collectiveprogramming.exercise14.repository;

import java.util.List;

import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.repository.MongoRepository;

import com.yamajun.collectiveprogramming.exercise14.model.processing.UserABSimilarity;

public interface UserABSimilarityRepository extends MongoRepository<UserABSimilarity, String>{

    List<UserABSimilarity> findByUserIdA(String userId, Pageable pageable);

}
