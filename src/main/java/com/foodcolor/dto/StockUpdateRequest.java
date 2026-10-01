package com.foodcolor.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class StockUpdateRequest {

    @NotNull(message = "El stock es obligatorio")
    @Min(value = 0, message = "El stock no puede ser negativo")
    private Integer stock;

    public StockUpdateRequest() {}

    public Integer getStock() { return stock; }
    public void setStock(Integer stock) { this.stock = stock; }
}