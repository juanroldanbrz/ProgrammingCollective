package com.yamajun.collectiveprogramming.exercise14.model.entity;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import lombok.Data;

@Data
@Document
public class Movie {
    
    @Id
    private String movieId;
    
    private String title;
    
    private String genres;
}
