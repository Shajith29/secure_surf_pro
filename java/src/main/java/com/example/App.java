package com.example;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;

import java.net.URI;
import java.net.http.*;
import java.net.http.HttpRequest.BodyPublishers;

import org.json.JSONObject;

public class App extends Application {

    private final HttpClient client = HttpClient.newHttpClient();
    private String predictionResult = "";  // Stores prediction result
    private String explanation = ""; // Stores explanation
    private String geminiExplanation = ""; // Stores Gemini explanation

    @Override
    public void start(Stage stage) {
        // Title
        Label title = new Label("🔐 SecureSurf URL Checker");
        title.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: #2C3E50;");

        // URL input
        TextField urlField = new TextField();
        urlField.setPromptText("Enter a URL to check");
        urlField.setPrefWidth(400);

        // Buttons
        Button checkButton = new Button("Check URL");
        Button explainButton = new Button("Explain");

        // Result display
        Label resultLabel = new Label();
        resultLabel.setStyle("-fx-font-size: 14px;");

        // Explanation TextArea (increased size)
        TextArea explanationTextArea = new TextArea();
        explanationTextArea.setPrefHeight(250);  // Increased height
        explanationTextArea.setWrapText(true);  // Wrap text
        explanationTextArea.setEditable(false);
        explanationTextArea.setStyle("-fx-font-size: 13px; -fx-text-fill: #333;");

        // RadioButtons for explanation choice
        ToggleGroup explanationGroup = new ToggleGroup();
        RadioButton regularExplanationButton = new RadioButton("Regular Explanation");
        RadioButton geminiExplanationButton = new RadioButton("Gemini Explanation");

        regularExplanationButton.setToggleGroup(explanationGroup);
        geminiExplanationButton.setToggleGroup(explanationGroup);
        regularExplanationButton.setSelected(true);  // Default option

        // Check button logic
        checkButton.setOnAction(e -> {
            String url = urlField.getText().trim();
            if (url.isEmpty()) {
                resultLabel.setText("⚠️ Please enter a URL.");
                resultLabel.setStyle("-fx-text-fill: orange;");
                return;
            }

            try {
                JSONObject json = new JSONObject();
                json.put("url", url);

                HttpRequest request = HttpRequest.newBuilder()
                        .uri(new URI("http://localhost:5000/predict"))
                        .header("Content-Type", "application/json")
                        .POST(BodyPublishers.ofString(json.toString()))
                        .build();

                client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                        .thenApply(HttpResponse::body)
                        .thenAccept(responseBody -> {
                            JSONObject responseJson = new JSONObject(responseBody);
                            predictionResult = responseJson.getString("result");
                            explanation = responseJson.getString("explanation");
                            geminiExplanation = responseJson.getString("gemini_explanation");

                            javafx.application.Platform.runLater(() -> {
                                // Update result label with phishing/safe status
                                if (predictionResult.equalsIgnoreCase("phishing")) {
                                    resultLabel.setText("🚨 Warning: This URL is *phishing*.");
                                    resultLabel.setStyle("-fx-text-fill: red; -fx-font-weight: bold;");
                                } else {
                                    resultLabel.setText("✅ This URL appears safe.");
                                    resultLabel.setStyle("-fx-text-fill: green; -fx-font-weight: bold;");
                                }

                                // Clear explanation text area initially
                                explanationTextArea.clear();
                            });
                        })
                        .exceptionally(ex -> {
                            ex.printStackTrace();
                            javafx.application.Platform.runLater(() -> resultLabel.setText("❌ Error connecting to server."));
                            return null;
                        });

            } catch (Exception ex) {
                resultLabel.setText("❌ Invalid URL format.");
                ex.printStackTrace();
            }
        });

        // Explain button logic
        explainButton.setOnAction(e -> {
            explanationTextArea.setText("🤔 Agent is thinking...");

            // Show explanation after clicking the "Explain" button
            new Thread(() -> {
                try {
                    Thread.sleep(1000);  // Simulate thinking time
                } catch (InterruptedException ex) {
                    ex.printStackTrace();
                }

                javafx.application.Platform.runLater(() -> {
                    if (regularExplanationButton.isSelected()) {
                        // Display regular explanation
                        String formattedExplanation = explanation.replace("\n", "\n\n");
                        explanationTextArea.setText(formattedExplanation);
                    } else if (geminiExplanationButton.isSelected()) {
                        // Remove the stars and format Gemini explanation
                        String formattedGeminiExplanation = geminiExplanation.replaceAll("\\*\\*.*?\\*\\*", "");
                        formattedGeminiExplanation = formattedGeminiExplanation.replace("\n", "\n\n");
                        explanationTextArea.setText(formattedGeminiExplanation);
                    } else {
                        explanationTextArea.setText("No explanation available yet.");
                    }
                });
            }).start();
        });

        // Layout
        VBox root = new VBox(15, title, urlField, checkButton, resultLabel, explainButton,
                regularExplanationButton, geminiExplanationButton, explanationTextArea);
        root.setStyle("-fx-padding: 30px; -fx-background-color: #FAFAFA; -fx-font-family: 'Segoe UI';");

        Scene scene = new Scene(root, 520, 550);  // Increased height to fit explanation
        stage.setTitle("SecureSurf");
        stage.setScene(scene);
        stage.show();
    }

    public static void main(String[] args) {
        launch();
    }
}
