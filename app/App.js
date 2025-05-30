import React, { useState, useRef } from "react";
import { View, Button, Image, Text, ActivityIndicator } from "react-native";
import { Camera } from "expo-camera";

export default function App() {
  const [hasPermission, setHasPermission] = useState(null);
  const [photoUri, setPhotoUri] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const cameraRef = useRef(null);

  React.useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === "granted");
    })();
  }, []);

  async function takePhotoAndSend() {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync({ base64: true });
      setPhotoUri(photo.uri);
      setLoading(true);

      // Prepare form data
      let formData = new FormData();
      formData.append("file", {
        uri: photo.uri,
        type: "image/jpeg",
        name: "photo.jpg",
      });

      try {
        const response = await fetch("http://localhost:8000/predict/", {
          method: "POST",
          body: formData,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        const json = await response.json();
        setResult(json);
      } catch (error) {
        console.error(error);
        setResult({ error: "Erro ao enviar a foto" });
      }

      setLoading(false);
    }
  }

  if (hasPermission === null) {
    return <View><Text>Solicitando permissão da câmera...</Text></View>;
  }
  if (hasPermission === false) {
    return <View><Text>Sem acesso à câmera</Text></View>;
  }

  return (
    <View style={{ flex: 1 }}>
      {!photoUri ? (
        <Camera style={{ flex: 1 }} ref={cameraRef}>
          <View style={{ flex: 1, justifyContent: "flex-end", marginBottom: 20 }}>
            <Button title="Tirar Foto" onPress={takePhotoAndSend} />
          </View>
        </Camera>
      ) : (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <Image source={{ uri: photoUri }} style={{ width: 300, height: 300 }} />
          {loading ? (
            <ActivityIndicator size="large" />
          ) : result ? (
            <View>
              {result.error ? (
                <Text>{result.error}</Text>
              ) : (
                <>
                  <Text>Modelo: {result.class}</Text>
                  <Text>Confiança: {(result.confidence * 100).toFixed(2)}%</Text>
                  {/* Aqui você pode expandir para mostrar mais detalhes do vape */}
                </>
              )}
              <Button title="Tirar outra foto" onPress={() => {
                setPhotoUri(null);
                setResult(null);
              }} />
            </View>
          ) : null}
        </View>
      )}
    </View>
  );
}
