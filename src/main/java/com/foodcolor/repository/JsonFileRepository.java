package com.foodcolor.repository;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Repository;
import org.springframework.util.FileCopyUtils;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReentrantReadWriteLock;

@Repository
public abstract class JsonFileRepository<T> {

    protected final ObjectMapper objectMapper;
    protected final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    protected List<T> data = new ArrayList<>();
    protected File file;

    @Value("${app.data.dir}")
    protected String dataDir;

    @Value("${app.products.file}")
    protected String productsFile;

    @Value("${app.orders.file}")
    protected String ordersFile;

    public JsonFileRepository() {
        this.objectMapper = new ObjectMapper();
        this.objectMapper.registerModule(new JavaTimeModule());
    }

    @PostConstruct
    public void init() {
        String filePath = getFilePath(productsFile, ordersFile);
        this.file = new File(dataDir, filePath);
        loadData();
    }

    protected abstract String getFilePath(String productsFile, String ordersFile);
    protected abstract TypeReference<List<T>> getTypeReference();

    public List<T> findAll() {
        lock.readLock().lock();
        try {
            return new ArrayList<>(data);
        } finally {
            lock.readLock().unlock();
        }
    }

    public T findById(Long id) {
        lock.readLock().lock();
        try {
            return data.stream()
                    .filter(item -> getId(item).equals(id))
                    .findFirst()
                    .orElse(null);
        } finally {
            lock.readLock().unlock();
        }
    }

    public T save(T entity) {
        lock.writeLock().lock();
        try {
            Long id = getId(entity);
            if (id == null || id == 0) {
                id = generateId();
                setId(entity, id);
            }
            final Long entityId = id;
            data.removeIf(item -> getId(item).equals(entityId));
            data.add(entity);
            persist();
            return entity;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void deleteById(Long id) {
        lock.writeLock().lock();
        try {
            data.removeIf(item -> getId(item).equals(id));
            persist();
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void update(T entity) {
        lock.writeLock().lock();
        try {
            Long id = getId(entity);
            data.removeIf(item -> getId(item).equals(id));
            data.add(entity);
            persist();
        } finally {
            lock.writeLock().unlock();
        }
    }

    protected void loadData() {
        lock.writeLock().lock();
        try {
            if (file.exists()) {
                try {
                    String content = FileCopyUtils.copyToString(
                            new java.io.FileReader(file, StandardCharsets.UTF_8));
                    data = objectMapper.readValue(content, getTypeReference());
                } catch (Exception e) {
                    data = new ArrayList<>();
                }
            } else {
                data = new ArrayList<>();
                persist();
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    protected void persist() {
        try {
            file.getParentFile().mkdirs();
            String json = objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(data);
            FileCopyUtils.copy(json, new java.io.FileWriter(file, StandardCharsets.UTF_8));
        } catch (IOException e) {
            throw new RuntimeException("Error guardando datos en " + file.getAbsolutePath(), e);
        }
    }

    protected abstract Long getId(T entity);
    protected abstract void setId(T entity, Long id);

    protected Long generateId() {
        return data.stream()
                .map(this::getId)
                .filter(id -> id != null)
                .max(Long::compareTo)
                .orElse(0L) + 1;
    }
}