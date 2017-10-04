package com.yamajun.collectiveprogramming.exercise14.model.processing;

import java.util.TreeMap;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import lombok.Data;

@Document
@Data
public class SimilarityToUserId {
    
    @Id
    private String userId;

    TreeMap<Double, String> similarityToUserId;

}
