package com.foodcolor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class FoodColorApplication {
    public static void main(String[] args) {
        SpringApplication.run(FoodColorApplication.class, args);
    }
}