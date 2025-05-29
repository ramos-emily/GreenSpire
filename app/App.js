import React, { useState, useRef } from "react";
import { StyleSheet, Text, View, Button, Image } from "react-native";
import { Camera } from "expo-camera";

export default function App() {
  const [hasPermission, setHasPermission] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const cameraRef = useRef(null);

  const pedirPermissao = async () => {
    const { status } = await Camera.requestCameraPermissionsAsync();
    setHasPermission(status === "granted");
  };

  const tirarFoto = async () => {
    if (cameraRef.current) {
      const foto = await cameraRef.current.takePictureAsync({ base64: false });
      setPhoto(foto.uri);
      enviarBackend(foto.uri);
    }
  };

  const enviarBackend = async (uri) => {
    const formData = new FormData();
    formData.append("file", {
      uri: uri,
      name: "foto.jpg",
      type: "image/jpeg",
    });

    try {
      const response = await fetch("http://192.168.0.X:8000/predict/", {  // ⚠️ Coloque o IP local do seu PC
        method: "POST",
        body: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const data = await response.json();
      setPrediction(data.class);
    } catch (error) {
      console.log("Erro:", error);
    }
  };

  if (hasPermission === null) {
    pedirPermissao();
    return <View />;
  }

  if (hasPermission === false) {
    return <Text>Sem acesso à câmera</Text>;
  }

  return (
    <View style={styles.container}>
      {photo ? (
        <Image source={{ uri: photo }} style={styles.preview} />
      ) : (
        <Camera style={styles.camera} ref={cameraRef} />
      )}

      <Button title="Tirar Foto" onPress={tirarFoto} />

      {prediction && (
        <Text style={styles.resultado}>É: {prediction}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center" },
  camera: { flex: 1 },
  preview: { flex: 1 },
  resultado: { fontSize: 20, textAlign: "center", margin: 20 },
});
