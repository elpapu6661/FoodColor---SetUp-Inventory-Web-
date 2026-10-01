package com.foodcolor.service;

import com.foodcolor.entity.Order;
import com.foodcolor.entity.Product;
import com.foodcolor.repository.OrderRepository;
import com.foodcolor.repository.ProductRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@Transactional
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductService productService;
    private final ProductRepository productRepository;

    public OrderService(OrderRepository orderRepository, ProductService productService, ProductRepository productRepository) {
        this.orderRepository = orderRepository;
        this.productService = productService;
        this.productRepository = productRepository;
    }

    public List<Order> getAllOrders() {
        return orderRepository.findAll();
    }

    public Order createOrder(String cliente, Long productoId, int cantidad) {
        Product product = productRepository.findById(productoId);
        if (product == null) {
            throw new IllegalArgumentException("Producto no encontrado");
        }

        if (cantidad > product.getStock()) {
            throw new IllegalArgumentException("Excede el stock del producto seleccionado");
        }

        boolean reduced = productService.reduceStock(productoId, cantidad);
        if (!reduced) {
            throw new IllegalStateException("No se pudo descontar el stock");
        }

        BigDecimal total = product.getPrecio().multiply(BigDecimal.valueOf(cantidad));
        
        Order order = new Order(
                cliente,
                product.getName(),
                product.getTipoUnidad(),
                cantidad,
                product.getPrecio(),
                total
        );
        order.setFecha(LocalDateTime.now());

        List<Order> orders = orderRepository.findAll();
        orders.add(order);
        orderRepository.saveAll(orders);

        return order;
    }

    public String formatOrderDate(LocalDateTime fecha) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
        return fecha.format(formatter);
    }
}