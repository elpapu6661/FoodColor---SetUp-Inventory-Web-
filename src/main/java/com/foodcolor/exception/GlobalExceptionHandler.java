package com.foodcolor.exception;

import com.foodcolor.dto.ErrorResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.NoHandlerFoundException;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationExceptions(
            MethodArgumentNotValidException ex, HttpServletRequest request) {
        
        Map<String, String> errors = new HashMap<>();
        for (FieldError error : ex.getBindingResult().getFieldErrors()) {
            errors.put(error.getField(), error.getDefaultMessage());
        }
        
        logger.warn("Validation error: {} - Path: {}", errors, request.getRequestURI());
        
        return ResponseEntity.badRequest()
                .body(new ErrorResponse(
                        "Error de validación",
                        HttpStatus.BAD_REQUEST.value(),
                        errors.toString(),
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ErrorResponse> handleConstraintViolation(
            ConstraintViolationException ex, HttpServletRequest request) {
        
        logger.warn("Constraint violation: {} - Path: {}", ex.getMessage(), request.getRequestURI());
        
        return ResponseEntity.badRequest()
                .body(new ErrorResponse(
                        "Error de validación",
                        HttpStatus.BAD_REQUEST.value(),
                        ex.getMessage(),
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ErrorResponse> handleHttpMessageNotReadable(
            HttpMessageNotReadableException ex, HttpServletRequest request) {
        
        logger.warn("Malformed JSON request: {} - Path: {}", ex.getMessage(), request.getRequestURI());
        
        return ResponseEntity.badRequest()
                .body(new ErrorResponse(
                        "Formato JSON inválido",
                        HttpStatus.BAD_REQUEST.value(),
                        "El cuerpo de la solicitud no es un JSON válido",
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<ErrorResponse> handleTypeMismatch(
            MethodArgumentTypeMismatchException ex, HttpServletRequest request) {
        
        logger.warn("Type mismatch: {} - Path: {}", ex.getMessage(), request.getRequestURI());
        
        String paramName = ex.getName();
        String expectedType = ex.getRequiredType() != null ? ex.getRequiredType().getSimpleName() : "desconocido";
        
        return ResponseEntity.badRequest()
                .body(new ErrorResponse(
                        "Parámetro inválido",
                        HttpStatus.BAD_REQUEST.value(),
                        String.format("El parámetro '%s' debe ser de tipo %s", paramName, expectedType),
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<ErrorResponse> handleMissingParameter(
            MissingServletRequestParameterException ex, HttpServletRequest request) {
        
        logger.warn("Missing parameter: {} - Path: {}", ex.getParameterName(), request.getRequestURI());
        
        return ResponseEntity.badRequest()
                .body(new ErrorResponse(
                        "Parámetro requerido faltante",
                        HttpStatus.BAD_REQUEST.value(),
                        String.format("El parámetro '%s' es obligatorio", ex.getParameterName()),
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgument(
            IllegalArgumentException ex, HttpServletRequest request) {
        
        logger.warn("Illegal argument: {} - Path: {}", ex.getMessage(), request.getRequestURI());
        
        return ResponseEntity.badRequest()
                .body(new ErrorResponse(
                        "Argumento inválido",
                        HttpStatus.BAD_REQUEST.value(),
                        ex.getMessage(),
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<ErrorResponse> handleIllegalState(
            IllegalStateException ex, HttpServletRequest request) {
        
        logger.warn("Illegal state: {} - Path: {}", ex.getMessage(), request.getRequestURI());
        
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(new ErrorResponse(
                        "Estado inválido",
                        HttpStatus.CONFLICT.value(),
                        ex.getMessage(),
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<ErrorResponse> handleBadCredentials(
            BadCredentialsException ex, HttpServletRequest request) {
        
        logger.warn("Bad credentials attempt from IP: {}", request.getRemoteAddr());
        
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(new ErrorResponse(
                        "Credenciales inválidas",
                        HttpStatus.UNAUTHORIZED.value(),
                        "Usuario o contraseña incorrectos",
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleAccessDenied(
            AccessDeniedException ex, HttpServletRequest request) {
        
        logger.warn("Access denied for IP: {} - Path: {}", request.getRemoteAddr(), request.getRequestURI());
        
        return ResponseEntity.status(HttpStatus.FORBIDDEN)
                .body(new ErrorResponse(
                        "Acceso denegado",
                        HttpStatus.FORBIDDEN.value(),
                        "No tiene permisos para acceder a este recurso",
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(NoHandlerFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            NoHandlerFoundException ex, HttpServletRequest request) {
        
        logger.warn("Endpoint not found: {} - Path: {}", ex.getRequestURL(), request.getRequestURI());
        
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(new ErrorResponse(
                        "Recurso no encontrado",
                        HttpStatus.NOT_FOUND.value(),
                        "El endpoint solicitado no existe",
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(DataAccessException.class)
    public ResponseEntity<ErrorResponse> handleDataAccess(
            DataAccessException ex, HttpServletRequest request) {
        
        logger.error("Database error: {} - Path: {}", ex.getMessage(), request.getRequestURI(), ex);
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ErrorResponse(
                        "Error de base de datos",
                        HttpStatus.INTERNAL_SERVER_ERROR.value(),
                        "Error al acceder a los datos. Intente nuevamente más tarde.",
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneric(
            Exception ex, HttpServletRequest request) {
        
        logger.error("Unexpected error: {} - Path: {}", ex.getMessage(), request.getRequestURI(), ex);
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ErrorResponse(
                        "Error interno del servidor",
                        HttpStatus.INTERNAL_SERVER_ERROR.value(),
                        "Ha ocurrido un error inesperado. Por favor, contacte al administrador.",
                        LocalDateTime.now(),
                        request.getRequestURI()
                ));
    }
}