package com.foodcolor.repository;

import com.foodcolor.entity.Product;
import org.springframework.stereotype.Repository;

import com.fasterxml.jackson.core.type.TypeReference;

import java.util.ArrayList;
import java.util.List;

@Repository
public class ProductRepository extends JsonFileRepository<Product> {

    @Override
    protected String getFilePath(String productsFile, String ordersFile) {
        return productsFile;
    }

    @Override
    protected TypeReference<List<Product>> getTypeReference() {
        return new TypeReference<>() {};
    }

    @Override
    protected Long getId(Product entity) {
        return entity.getId();
    }

    @Override
    protected void setId(Product entity, Long id) {
        entity.setId(id);
    }

    public Product findByNameIgnoreCase(String name) {
        lock.readLock().lock();
        try {
            return data.stream()
                    .filter(p -> p.getName().equalsIgnoreCase(name))
                    .findFirst()
                    .orElse(null);
        } finally {
            lock.readLock().unlock();
        }
    }

    public List<Product> findByCategory(String category) {
        lock.readLock().lock();
        try {
            if ("all".equalsIgnoreCase(category) || category == null) {
                return new ArrayList<>(data);
            }
            return data.stream()
                    .filter(p -> category.equalsIgnoreCase(p.getCategory()))
                    .toList();
        } finally {
            lock.readLock().unlock();
        }
    }

    public List<Product> search(String query, String category) {
        lock.readLock().lock();
        try {
            return data.stream()
                    .filter(p -> category == null || "all".equalsIgnoreCase(category) || category.equalsIgnoreCase(p.getCategory()))
                    .filter(p -> query == null || query.isEmpty() || 
                            p.getName().toLowerCase().contains(query.toLowerCase()))
                    .toList();
        } finally {
            lock.readLock().unlock();
        }
    }
}