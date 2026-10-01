package com.foodcolor.dto;

import java.time.LocalDateTime;

public class ErrorResponse {
    private String error;
    private int status;
    private String message;
    private LocalDateTime timestamp;
    private String path;
    private int disponible;

    public ErrorResponse() {}

    public ErrorResponse(String error) {
        this.error = error;
    }

    public ErrorResponse(String error, int disponible) {
        this.error = error;
        this.disponible = disponible;
    }

    public ErrorResponse(String error, int status, String message, LocalDateTime timestamp, String path) {
        this.error = error;
        this.status = status;
        this.message = message;
        this.timestamp = timestamp;
        this.path = path;
    }

    public String getError() { return error; }
    public void setError(String error) { this.error = error; }

    public int getStatus() { return status; }
    public void setStatus(int status) { this.status = status; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }

    public String getPath() { return path; }
    public void setPath(String path) { this.path = path; }

    public int getDisponible() { return disponible; }
    public void setDisponible(int disponible) { this.disponible = disponible; }
}