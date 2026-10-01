package com.foodcolor.service;

import com.foodcolor.entity.Product;
import com.foodcolor.repository.ProductRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class ProductService {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public List<Product> getAllProducts() {
        return productRepository.findAll();
    }

    public List<Product> getProductsByCategory(String category) {
        return productRepository.findByCategory(category);
    }

    public List<Product> searchProducts(String query, String category) {
        return productRepository.search(query, category);
    }

    public Product getProductById(Long id) {
        return productRepository.findById(id);
    }

    public Product createOrUpdateProduct(Product product) {
        Product existing = productRepository.findByNameIgnoreCase(product.getName());
        
        if (existing != null) {
            existing.setStock(existing.getStock() + product.getStock());
            existing.setPrecio(product.getPrecio());
            if (product.getTipoUnidad() != null && !product.getTipoUnidad().isBlank()) {
                existing.setTipoUnidad(product.getTipoUnidad());
            }
            if (product.getCategory() != null && !product.getCategory().isBlank()) {
                existing.setCategory(product.getCategory());
            }
            if (product.getDesc() != null && !product.getDesc().isBlank()) {
                existing.setDesc(product.getDesc());
            }
            existing.updateTimestamp();
            return productRepository.save(existing);
        } else {
            product.setId(null);
            return productRepository.save(product);
        }
    }

    public boolean reduceStock(Long productId, int quantity) {
        Product product = productRepository.findById(productId);
        if (product == null) {
            return false;
        }
        if (product.getStock() < quantity) {
            return false;
        }
        product.setStock(product.getStock() - quantity);
        product.updateTimestamp();
        productRepository.save(product);
        return true;
    }

    public int getStock(Long productId) {
        Product product = productRepository.findById(productId);
        return product != null ? product.getStock() : 0;
    }

    public long countProducts() {
        return productRepository.findAll().size();
    }
}