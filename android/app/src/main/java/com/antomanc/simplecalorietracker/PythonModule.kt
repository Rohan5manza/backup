package com.antomanc.simplecalorietracker;

import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.bridge.WritableNativeMap;
import com.chaquo.python.PyException;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;

public class PythonModule extends ReactContextBaseJavaModule {

    public PythonModule(ReactApplicationContext reactContext) {
        super(reactContext);
        // Initialize Python if needed
        if (!Python.isStarted()) {
            Python.start(new com.chaquo.python.android.AndroidPlatform(reactContext));
        }
    }

    override fun getName(): String {
        Log.d("PythonModule", "Module registered as: PythonModule")
        return "PythonModule"
    }

    @ReactMethod
    public void detectFood(String base64Image, Promise promise) {
        try {
            Log.d("PythonModule", "Python started: " + Python.isStarted());
            Python py = Python.getInstance();
            PyObject detector = py.getModule("detector");
            PyObject result = detector.callAttr("detect_food", base64Image);
            
            // Convert PyObject to WritableMap
            WritableMap writableMap = new WritableNativeMap();
            PyObject keys = result.callAttr("keys");
            
            for (PyObject key : keys.asList()) {
                String keyStr = key.toString();
                PyObject value = result.get(key);
                
                if (value.toJava(String.class) != null) {
                    writableMap.putString(keyStr, value.toString());
                } else if (value.toJava(Integer.class) != null) {
                    writableMap.putInt(keyStr, value.toJava(Integer.class));
                } else if (value.toJava(Double.class) != null) {
                    writableMap.putDouble(keyStr, value.toJava(Double.class));
                } else if (value.toJava(Boolean.class) != null) {
                    writableMap.putBoolean(keyStr, value.toJava(Boolean.class));
                }
            }
            
            promise.resolve(writableMap);
        } catch (PyException e) {
            promise.reject("PYTHON_ERROR", e.getMessage(), e);
        } catch (Exception e) {
            Log.e("PythonModule", "Error:", e);
            promise.reject("UNEXPECTED_ERROR", e.getMessage(), e);
        }
    }
}