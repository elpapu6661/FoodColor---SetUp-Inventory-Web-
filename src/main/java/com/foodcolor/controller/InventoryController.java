package com.foodcolor.controller;

import com.foodcolor.dto.OrderRequest;
import com.foodcolor.dto.OrderResponse;
import com.foodcolor.dto.ProductRequest;
import com.foodcolor.dto.ProductResponse;
import com.foodcolor.dto.StockUpdateRequest;
import com.foodcolor.entity.Order;
import com.foodcolor.entity.Product;
import com.foodcolor.repository.ProductRepository;
import com.foodcolor.service.OrderService;
import com.foodcolor.service.ProductService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/inventory")
public class InventoryController {

    private final ProductService productService;
    private final OrderService orderService;
    private final ProductRepository productRepository;

    public InventoryController(ProductService productService, OrderService orderService, ProductRepository productRepository) {
        this.productService = productService;
        this.orderService = orderService;
        this.productRepository = productRepository;
    }

    @GetMapping("/productos")
    public ResponseEntity<List<Product>> getAllProducts() {
        return ResponseEntity.ok(productService.getAllProducts());
    }

    @PostMapping("/productos")
    public ResponseEntity<ProductResponse> createOrUpdateProduct(@Valid @RequestBody ProductRequest request) {
        Product product = new Product();
        product.setName(request.getName());
        product.setCategory(request.getCategory());
        product.setDesc(request.getDesc());
        product.setImg(request.getImg());
        product.setPrecio(request.getPrecio());
        product.setStock(request.getStock());
        product.setTipoUnidad(request.getTipoUnidad());

        Product saved = productService.createOrUpdateProduct(product);
        
        Product existing = productService.getAllProducts().stream()
                .filter(p -> p.getName().equalsIgnoreCase(request.getName()))
                .findFirst()
                .orElse(null);
        
        boolean isUpdate = existing != null && existing.getId().equals(saved.getId()) 
                && productService.getAllProducts().stream()
                    .filter(p -> p.getName().equalsIgnoreCase(request.getName()))
                    .count() == 1;

        String mensaje = isUpdate ? "Stock actualizado" : "Producto creado";
        int status = isUpdate ? 200 : 201;
        
        return ResponseEntity.status(status)
                .body(new ProductResponse(mensaje, saved));
    }

    @GetMapping("/pedidos")
    public ResponseEntity<List<Order>> getAllOrders() {
        return ResponseEntity.ok(orderService.getAllOrders());
    }

    @PostMapping("/pedidos")
    public ResponseEntity<OrderResponse> createOrder(@Valid @RequestBody OrderRequest request) {
        Order order = orderService.createOrder(
                request.getCliente(),
                request.getProductoId(),
                request.getCantidad()
        );
        
        int stockRestante = productService.getStock(request.getProductoId());
        
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(new OrderResponse("Pedido creado", order, stockRestante));
    }

    @PutMapping("/productos/{id}/stock")
    public ResponseEntity<ProductResponse> updateStock(@PathVariable Long id, @Valid @RequestBody StockUpdateRequest request) {
        Product product = productService.getProductById(id);
        if (product == null) {
            throw new IllegalArgumentException("Producto no encontrado");
        }
        product.setStock(request.getStock());
        product.updateTimestamp();
        productRepository.save(product);
        return ResponseEntity.ok(new ProductResponse("Stock actualizado", product));
    }
}