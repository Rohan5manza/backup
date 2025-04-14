package com.yourproject

import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod
import com.facebook.react.bridge.Promise
import com.chaquo.python.PyObject
import com.chaquo.python.Python

class PythonModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {
    override fun getName() = "PythonModule"

    @ReactMethod
    fun detectFood(imageBase64: String, promise: Promise) {
        try {
            val py: PyObject = Python.getInstance().getModule("detector")
            val result: String = py.callAttr("detect", imageBase64).toString()
            promise.resolve(result)
        } catch (e: Exception) {
            promise.reject("PYTHON_ERROR", e.message)
        }
    }
}