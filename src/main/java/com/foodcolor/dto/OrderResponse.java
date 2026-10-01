package com.foodcolor.dto;

import com.foodcolor.entity.Order;

public class OrderResponse {
    private String mensaje;
    private Order boleta;
    private int stockRestante;

    public OrderResponse() {}

    public OrderResponse(String mensaje, Order boleta, int stockRestante) {
        this.mensaje = mensaje;
        this.boleta = boleta;
        this.stockRestante = stockRestante;
    }

    public String getMensaje() { return mensaje; }
    public void setMensaje(String mensaje) { this.mensaje = mensaje; }

    public Order getBolet() { return boleta; }
    public void setBolet(Order boleta) { this.boleta = boleta; }

    public int getStockRestante() { return stockRestante; }
    public void setStockRestante(int stockRestante) { this.stockRestante = stockRestante; }
}