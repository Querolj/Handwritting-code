package sample;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

import javafx.scene.image.Image;


import java.io.*;
import java.util.Optional;
import java.util.logging.Logger;

public class InterfaceTest extends Application {

    File selectedFile;
    String nameFile, concatLine;

    @Override
    public void start(Stage primaryStage) throws Exception {
        /*  http://www-acad.sheridanc.on.ca/~jollymor/prog24178/javafx3b.html */

        GridPane gridPane = new GridPane();



        gridPane.setVgap(10);
        gridPane.setHgap(20);
        gridPane.setGridLinesVisible(true);
        gridPane.setPadding(new Insets(25, 25, 25, 25));

        BorderPane root = new BorderPane();
        MenuBar menuBar = new MenuBar();
        menuBar.prefWidthProperty().bind(primaryStage.widthProperty());
        root.setTop(menuBar);
        root.setCenter(gridPane);

        Menu profileMenu = new Menu("Profile");
        MenuItem profileNewMenuItem = new MenuItem("Nouveau profile");
        MenuItem profileSaveMenuItem = new MenuItem("Charger un profile");

        profileMenu.getItems().addAll(profileNewMenuItem, profileSaveMenuItem);

        profileNewMenuItem.setOnAction(event -> {
            TextInputDialog dialog = new TextInputDialog();
            dialog.setTitle("profile manager");
            dialog.setHeaderText("Création d'un nouveau profil");
            dialog.setContentText("Entrez le nom du profile:");

            Optional<String> result = dialog.showAndWait();
            result.ifPresent(name -> System.out.println("Your name: " + name));
        });

        Menu fileMenu = new Menu("Fichier");
        MenuItem saveMenuItem = new MenuItem("Sauvegarder");
        MenuItem exitMenuItem = new MenuItem("Quitter");

        exitMenuItem.setOnAction(actionEvent -> Platform.exit());
        saveMenuItem.setOnAction(event -> {
            FileChooser fileChooser = new FileChooser();

            //Set extension filter for text files
            FileChooser.ExtensionFilter extFilter = new FileChooser.ExtensionFilter("TXT files (*.txt)", "*.txt");
            fileChooser.getExtensionFilters().add(extFilter);

            //Show save file dialog
            File file = fileChooser.showSaveDialog(primaryStage);

            if (file != null) {
                saveTextToFile(concatLine, file);
            }
        });

        fileMenu.getItems().addAll(saveMenuItem,
                new SeparatorMenuItem(), exitMenuItem);

        menuBar.getMenus().addAll(fileMenu,profileMenu);

        ColumnConstraints columnConstraints = new ColumnConstraints();
        columnConstraints.setPercentWidth(33.3);

        gridPane.getColumnConstraints().addAll(columnConstraints, columnConstraints, columnConstraints);

        Button openFile = new Button("Ouvrir");
        Button btnRead = new Button("Lire");
        Button btnOk = new Button("Process");
        Button btnEdit = new Button("Edit");


        ChoiceBox language = new ChoiceBox(FXCollections.observableArrayList("Java", "C", "C++"));
        language.getSelectionModel().selectFirst();
        language.setMaxWidth(Double.MAX_VALUE);

        HBox hboxResultats = new HBox();
        hboxResultats.setSpacing(2);

        HBox hBoxArguments = new HBox();
        hBoxArguments.setSpacing(2);


        Label labelArgsLanguage = new Label("ARGUMENTS: ");
        Label labelResultPicture = new Label("RESULTAT: ");
        TextField tfArgsLanguage = new TextField();
        TextArea taResult = new TextArea();
        taResult.setText("");
        taResult.setDisable(false);
        GridPane.setFillWidth(taResult, true);

        hBoxArguments.getChildren().add(labelArgsLanguage);
        hBoxArguments.getChildren().add(tfArgsLanguage);

        /* SETUP BORDER PANE */
        VBox[] vBoxes = new VBox[3];
        for (int i = 0; i < 3; i++) {
            vBoxes[i] = new VBox();
        }
        vBoxes[0].getChildren().add(openFile);

        gridPane.add(vBoxes[0], 0, 0, 1, 1);

        gridPane.add(btnRead,1,0,1, 1);
        gridPane.add(labelResultPicture,1,1, 1, 1);
        gridPane.add(taResult,1,1);
        gridPane.add(hboxResultats,1,1, 2, 1);
        gridPane.add(btnEdit, 1, 2, 2, 1);

        gridPane.add(language,2,0, 3, 1);
        gridPane.add(hBoxArguments,2,1, 3, 1);
        gridPane.add(btnOk,2,2, 3, 2);




        /* SETUP BUTTON */
        openFile.setMaxWidth(Double.MAX_VALUE);
        openFile.setOnAction(event -> {
            FileChooser fileChooser = new FileChooser();
            fileChooser.setTitle("Ouvrir une image");
            fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Image Files", "*.png", "*.jpg", "*.jpeg", "*.bmp"));
            selectedFile = fileChooser.showOpenDialog(primaryStage);
            if (selectedFile != null) {
                Image image = new Image(selectedFile.toURI().toString());
                ImageView iv2 = new ImageView();
                iv2.setImage(image);
                iv2.setFitWidth(295);
                iv2.setPreserveRatio(true);
                iv2.setSmooth(true);
                iv2.setCache(true);
                gridPane.add(iv2,0,1,2,2);
            }
        });

        btnEdit.setOnAction(event -> {
            FileChooser fileChooser = new FileChooser();
            fileChooser.setTitle("Editer avec une application");
            fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("All Files", "*.*"));
            File selectedApp = fileChooser.showOpenDialog(primaryStage);
            if (selectedApp != null) {
                try {
                    Runtime r = Runtime.getRuntime();
                    Process p = null;
                    p = r.exec(selectedApp.getName().substring(0, selectedApp.getName().lastIndexOf('.'))+" "+nameFile);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        });

        btnOk.setMaxWidth(Double.MAX_VALUE);
        btnOk.setOnAction(event -> {

            try {
                Process p = null;
                String stringLanguage = "";
                Runtime r = Runtime.getRuntime();
                p = r.exec("ls");
                BufferedReader b = new BufferedReader(new InputStreamReader(p.getInputStream()));
                String line = "";

                /*switch ((String) language.getValue()) {
                    case "Java":
                        stringLanguage = "Javac";
                        break;
                    case "C":
                        stringLanguage = "gcc";
                        break;
                    case "C++":
                        stringLanguage = "g++";
                }*/


                //p = r.exec(stringLanguage);
                p.waitFor();
                while ((line = b.readLine()) != null) {
                    System.out.println(line);
                }

                b.close();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });


        btnRead.setMaxWidth(Double.MAX_VALUE);
        btnRead.setOnAction(event -> {
            try {
                nameFile = selectedFile.getName().substring(0, selectedFile.getName().lastIndexOf('.'))+".txt";
                File f = new File(nameFile);
                f.createNewFile();
                PrintWriter out = new PrintWriter(f);
                ProcessBuilder builder = new ProcessBuilder("pwd");
                //ProcessBuilder builder = new ProcessBuilder("python3 /Users/Matthew/Documents/Handwriting/handwritting-code/main.py -rd "+selectedFile.getPath());
                builder.redirectErrorStream(true);
                Process process = builder.start();
                InputStream is = process.getInputStream();
                BufferedReader reader = new BufferedReader(new InputStreamReader(is));
                String line = "";
                concatLine = "";
                while ((line = reader.readLine()) != null) {
                    concatLine += line;
                }
                out.println(concatLine);
                taResult.setText(concatLine);
                out.close();
                reader.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        });

        primaryStage.setTitle("Hand writting project");
        primaryStage.setScene(new Scene(root, 1000, 500));
        primaryStage.show();
    }

    private void saveTextToFile(String content, File file) {
        try {
            PrintWriter writer;
            writer = new PrintWriter(file);
            writer.println(content);
            writer.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }


    public static void main(String[] args) {
        launch(args);
    }
}
