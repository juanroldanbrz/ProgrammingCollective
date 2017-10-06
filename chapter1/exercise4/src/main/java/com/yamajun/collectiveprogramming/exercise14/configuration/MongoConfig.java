package com.yamajun.collectiveprogramming.exercise14.configuration;

import org.springframework.context.annotation.Configuration;


@Configuration
public class MongoConfig {
    
    private static final String MONGO_DB_URL = "localhost";
    private static final String MONGO_DB_NAME = "embeded_db";

}