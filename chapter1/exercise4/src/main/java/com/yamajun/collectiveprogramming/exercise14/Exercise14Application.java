package com.yamajun.collectiveprogramming.exercise14;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;

import com.github.mongobee.Mongobee;

@EnableMongoRepositories
@SpringBootApplication
public class Exercise14Application {

	@Bean
	public Mongobee mongobee(){
		Mongobee runner = new Mongobee("mongodb://localhost:27017/exercise14");
		runner.setChangeLogsScanPackage("com.yamajun.collectiveprogramming.exercise14.bootstrap");
		return runner;
	}

	public static void main(String[] args) {
		SpringApplication.run(Exercise14Application.class, args);
	}
}
