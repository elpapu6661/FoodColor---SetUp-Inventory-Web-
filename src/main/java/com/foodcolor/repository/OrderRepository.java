package com.foodcolor.repository;

import com.foodcolor.entity.Order;
import org.springframework.stereotype.Repository;

import com.fasterxml.jackson.core.type.TypeReference;

import java.util.ArrayList;
import java.util.List;

@Repository
public class OrderRepository extends JsonFileRepository<Order> {

    @Override
    protected String getFilePath(String productsFile, String ordersFile) {
        return ordersFile;
    }

    @Override
    protected TypeReference<List<Order>> getTypeReference() {
        return new TypeReference<>() {};
    }

    @Override
    protected Long getId(Order entity) {
        return null;
    }

    @Override
    protected void setId(Order entity, Long id) {
    }

    @Override
    protected Long generateId() {
        return System.currentTimeMillis();
    }

    public void saveAll(List<Order> orders) {
        lock.writeLock().lock();
        try {
            this.data = new ArrayList<>(orders);
            persist();
        } finally {
            lock.writeLock().unlock();
        }
    }
}