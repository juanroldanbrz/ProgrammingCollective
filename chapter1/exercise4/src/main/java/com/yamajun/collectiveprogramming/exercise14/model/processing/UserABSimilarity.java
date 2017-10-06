package com.yamajun.collectiveprogramming.exercise14.model.processing;

import org.springframework.data.mongodb.core.mapping.Document;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
@Document
public class UserABSimilarity {
    
    private String userIdA;
    private String userIdB;
    private Double similarity;
}
