package com.foodcolor.dto;

import com.foodcolor.entity.Product;

public class ProductResponse {
    private String mensaje;
    private Product producto;
    private int stockRestante;

    public ProductResponse() {}

    public ProductResponse(String mensaje, Product producto) {
        this.mensaje = mensaje;
        this.producto = producto;
    }

    public ProductResponse(String mensaje, Product producto, int stockRestante) {
        this.mensaje = mensaje;
        this.producto = producto;
        this.stockRestante = stockRestante;
    }

    public String getMensaje() { return mensaje; }
    public void setMensaje(String mensaje) { this.mensaje = mensaje; }

    public Product getProducto() { return producto; }
    public void setProducto(Product producto) { this.producto = producto; }

    public int getStockRestante() { return stockRestante; }
    public void setStockRestante(int stockRestante) { this.stockRestante = stockRestante; }
}