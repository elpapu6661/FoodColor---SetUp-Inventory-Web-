package com.foodcolor.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import java.math.BigDecimal;

public class ProductRequest {

    @NotBlank(message = "El nombre es obligatorio")
    private String name;

    private String category = "colorantes";

    private String desc = "";

    private String img = "";

    @NotNull(message = "El precio es obligatorio")
    @PositiveOrZero(message = "El precio no puede ser negativo")
    private BigDecimal precio;

    @Min(value = 1, message = "La cantidad debe ser mayor a 0")
    private Integer stock = 0;

    private String tipoUnidad = "";

    public ProductRequest() {}

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getDesc() { return desc; }
    public void setDesc(String desc) { this.desc = desc; }

    public String getImg() { return img; }
    public void setImg(String img) { this.img = img; }

    public BigDecimal getPrecio() { return precio; }
    public void setPrecio(BigDecimal precio) { this.precio = precio; }

    public Integer getStock() { return stock; }
    public void setStock(Integer stock) { this.stock = stock; }

    public String getTipoUnidad() { return tipoUnidad; }
    public void setTipoUnidad(String tipoUnidad) { this.tipoUnidad = tipoUnidad; }
}