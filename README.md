# Code for Master Thesis

## Introduction

This repository includes all the code used for my Master thesis. The goal of the thesis is to predict GDP values from European NUTS 2 regions with respective satellite images from Earth Engine. CNN models were trained on the satellite images to obtain predictions.

## Content

The code is divided into four main folders, which each include code for a separate part of the thesis:

| Folder | Description  |
|---|---|
| CleanExploreData  | Scripts to clean, wrangle and explore the raw GDP Data  |
| ImageExport  | Script to export satellite imges from Earth Engine  |
| NeuralNetTrain  | Scripts to prepare input data and train CNN models  |
| ResultAnalyse  | Scripts to analyse the results |

## General Comments

The data pipeline for this project is quite complex as data was combined from different sources and saved into different folders. Thus, the code highly depends on the correct file paths, which are naturally very specific for my user. Without specifying the correct paths in the code, most of the code will not run.

Further, the satellite images were saved to my Google Drive as this is the only way (known to me) to export satellite imagery from Earth Engine.

## Coding Languages

In this project, three different file types were used to include code. 
  1. .py - Mainly used to prepare data and write functions to be used in jupyter notebooks
  2. .ipynb - Jupyter Notebooks were used for data exploration, visualising data and training the CNN models
  3. .R - R was mainly used for visualisation as ggplot produces beautiful plots
