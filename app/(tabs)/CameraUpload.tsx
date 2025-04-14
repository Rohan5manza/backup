import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Text, ActivityIndicator, Image } from 'react-native';
import { Button, Icon } from 'react-native-elements';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
import { NativeModules } from 'react-native';

// Define the result type explicitly
type DetectionResult = {
    category: string;
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
};

export default function FoodScannerScreen({ navigation }: { navigation: any }) {
    const [image, setImage] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [result, setResult] = useState<DetectionResult | null>(null);

    useEffect(() => {
        (async () => {
            const { status } = await ImagePicker.requestCameraPermissionsAsync();
            if (status !== 'granted') {
                alert('Camera permission is required for food scanning!');
            }
        })();
    }, []);

    const processImage = async (uri: string) => {
        setLoading(true);
        try {
            const base64 = await FileSystem.readAsStringAsync(uri, {
                encoding: FileSystem.EncodingType.Base64,
            });

            // Actual call to native Python module
            // const response = await NativeModules.PythonModule.detectFood(base64);
            // const data = JSON.parse(response);
            // setResult(data);

            // Simulated for now
            setTimeout(() => {
                setResult({
                    category: 'Apple',
                    calories: 95,
                    protein: 0.5,
                    carbs: 25,
                    fats: 0.3,
                });
                setLoading(false);
            }, 1500);
        } catch (error) {
            setLoading(false);
            alert('Error processing image');
        }
    };

    const pickImageFromCamera = async () => {
        const result = await ImagePicker.launchCameraAsync({
            allowsEditing: false,
            quality: 0.8,
        });
        if (!result.canceled) {
            const uri = result.assets[0].uri;
            setImage(uri);
            await processImage(uri);
        }
    };

    const pickImageFromGallery = async () => {
        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            quality: 0.8,
        });
        if (!result.canceled) {
            const uri = result.assets[0].uri;
            setImage(uri);
            await processImage(uri);
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.buttonGroup}>
                <Button
                    icon={<Icon name="camera" type="font-awesome" color="white" />}
                    title=" Take Photo"
                    buttonStyle={styles.button}
                    onPress={pickImageFromCamera}
                />
                <Button
                    icon={<Icon name="photo" type="material" color="white" />}
                    title=" From Gallery"
                    buttonStyle={styles.button}
                    onPress={pickImageFromGallery}
                />
            </View>

            {loading && <ActivityIndicator size="large" style={styles.loader} />}
            {image && <Image source={{ uri: image }} style={{ width: 200, height: 200, marginBottom: 20 }} />}

            {result && (
                <View style={styles.resultContainer}>
                    <Text style={styles.resultTitle}>Nutrition Information</Text>
                    <Text>Food: {result.category}</Text>
                    <Text>Calories: {result.calories} kcal</Text>
                    <Text>Protein: {result.protein}g</Text>
                    <Text>Carbs: {result.carbs}g</Text>
                    <Text>Fats: {result.fats}g</Text>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#f5f5f5',
    },
    buttonGroup: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        marginBottom: 20,
    },
    button: {
        backgroundColor: '#4CAF50',
        borderRadius: 8,
        paddingVertical: 12,
        paddingHorizontal: 16,
    },
    loader: {
        marginVertical: 20,
    },
    resultContainer: {
        backgroundColor: 'white',
        padding: 20,
        borderRadius: 10,
        marginTop: 20,
    },
    resultTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
});
