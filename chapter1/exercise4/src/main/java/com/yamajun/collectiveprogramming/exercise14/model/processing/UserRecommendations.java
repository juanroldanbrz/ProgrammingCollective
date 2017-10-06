package com.yamajun.collectiveprogramming.exercise14.model.processing;

import org.springframework.data.mongodb.core.mapping.Document;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
@Document
public class UserRecommendations {
    
    private String userId;
    private String movieId;
    private String movieName;
    private Double recommendationScore;
}
