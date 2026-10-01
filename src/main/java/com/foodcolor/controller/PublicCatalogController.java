package com.foodcolor.controller;

import com.foodcolor.dto.ContactRequest;
import com.foodcolor.dto.ContactResponse;
import com.foodcolor.entity.Product;
import com.foodcolor.service.ProductService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/public")
public class PublicCatalogController {

    private static final Logger logger = LoggerFactory.getLogger(PublicCatalogController.class);
    private final ProductService productService;

    public PublicCatalogController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping("/productos")
    public ResponseEntity<List<Product>> getProducts(
            @RequestParam(value = "category", defaultValue = "all") String category,
            @RequestParam(value = "q", defaultValue = "") String search) {
        
        try {
            List<Product> products;
            if (search != null && !search.isBlank()) {
                products = productService.searchProducts(search, category);
            } else {
                products = productService.getProductsByCategory(category);
            }
            return ResponseEntity.ok(products);
        } catch (Exception ex) {
            logger.error("Error fetching products: {}", ex.getMessage(), ex);
            throw ex;
        }
    }

    @PostMapping("/contact")
    public ResponseEntity<ContactResponse> contact(@Valid @RequestBody ContactRequest request) {
        logger.info("New contact request from: {} - {}", request.getName(), request.getEmail());
        return ResponseEntity.ok(new ContactResponse(true));
    }
}