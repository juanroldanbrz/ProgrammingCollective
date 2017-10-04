package com.yamajun.collectiveprogramming.exercise14.model.entity;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import lombok.Data;

@Data
@Document
public class Rating {

    @Id
    private String _id;

    private String userId;

    private String movieId;

    private Float rating;

    private String timestamp;

    @Override
    public boolean equals(Object that) {
        return this == that || !(that instanceof Rating) || ((Rating) that).getMovieId().equals(this.getMovieId());

    }
}
