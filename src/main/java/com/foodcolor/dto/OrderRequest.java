package com.foodcolor.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class OrderRequest {

    @NotBlank(message = "El nombre del cliente es obligatorio")
    private String cliente;

    @NotNull(message = "El ID del producto es obligatorio")
    private Long productoId;

    @Min(value = 1, message = "La cantidad debe ser mayor a 0")
    private Integer cantidad;

    public OrderRequest() {}

    public String getCliente() { return cliente; }
    public void setCliente(String cliente) { this.cliente = cliente; }

    public Long getProductoId() { return productoId; }
    public void setProductoId(Long productoId) { this.productoId = productoId; }

    public Integer getCantidad() { return cantidad; }
    public void setCantidad(Integer cantidad) { this.cantidad = cantidad; }
}