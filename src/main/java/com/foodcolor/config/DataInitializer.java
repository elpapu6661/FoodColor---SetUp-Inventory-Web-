package com.foodcolor.config;

import com.foodcolor.entity.Product;
import com.foodcolor.repository.ProductRepository;
import com.foodcolor.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

@Component
@Profile("!test")
public class DataInitializer implements CommandLineRunner {

    private final ProductRepository productRepository;
    private final OrderRepository orderRepository;

    @Value("${app.products.file}")
    private String productsFilePath;

    @Value("${app.orders.file}")
    private String ordersFilePath;

    public DataInitializer(ProductRepository productRepository, OrderRepository orderRepository) {
        this.productRepository = productRepository;
        this.orderRepository = orderRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        Path productsPath = Path.of(productsFilePath);
        Path ordersPath = Path.of(ordersFilePath);

        if (!Files.exists(productsPath)) {
            initializeSampleProducts();
        }

        if (!Files.exists(ordersPath)) {
            orderRepository.saveAll(List.of());
        }
    }

    private void initializeSampleProducts() {
        List<Product> products = List.of(
                new Product("Colorante Rojo Carmín #40", "colorantes", 
                        "Colorante natural intenso para lácteos y bebidas.", "",
                        new BigDecimal("5000"), 12, "250g"),
                new Product("Azul Profundo #3910", "colorantes",
                        "Colorante azul intenso para repostería y bebidas.", "",
                        new BigDecimal("3200"), 13, "600g"),
                new Product("Rosado Maricon #ELP", "colorantes",
                        "Colorante rosado para aplicaciones especiales.", "",
                        new BigDecimal("60000"), 25, "1000g"),
                new Product("Esencia de Vainilla", "esencias",
                        "Esencia concentrada para repostería.", "",
                        new BigDecimal("4500"), 20, "100ml"),
                new Product("Aditivo Conservante E-211", "aditivos",
                        "Conservante para prolongar vida útil.", "",
                        new BigDecimal("2800"), 30, "500g")
        );

        products.forEach(productRepository::save);
    }
}