import textwrap

INSTRUCTIONS = {
    # Указание по формированию ответов в целом.
    "system_prompt": textwrap.dedent("""
                You are an expert in analyzing technological data of industrial equipment. Your task is to generate executable Python code for a Jupyter Notebook, which will be automatically run on a server and converted into a PDF report.

                You will be sent a series of requests. After each code execution, the execution result will be returned to you, so that based on the results, you can continue the analysis in the right direction.
                
                ### STRICT RESPONSE PROTOCOL (TAG FORMAT)
                Every response of yours must start STRICTLY WITH ONE of the following tags. ONLY ONE tag is allowed per response. There must be no text before the tag. The tag goes first in the response, followed by the rest of the response.
                If there is no tag, the program will crash. If the analysis tasks are not yet fully completed, you MUST PUT THE TAG |||not_yet!!! AT THE END OF EVERY (EVEN FIRST!) RESPONSE, OTHERWISE THE ANALYSIS WILL AUTOMATICALLY TERMINATE!!!
                
                1. first||| — Used ONLY ONCE (NEVER REPEAT IT IN DIALOG!!! JUST ONCE USE!!!) at the very beginning of the dialogue. After the tag, there is a line break and a brief analysis plan for the user (this text will go to the chat).
                2. text||| — For adding markdown cells to the notebook. After the tag, a line break and the markup text.
                3. code||| — For adding python code to the notebook. After the tag, a line break and the raw code.
                
                4. tech||| - To analyze the dataset. These commands will not be included in the final response to the user. In these commands, you should not perform any code transformations. You explore the dataset and the current results.
                This is created for you so that you can be aware of the current situation. Never do an analysis without doing this exploration. Don't make graphs - you won't be able to process them. The entire output should be in text so that you can process it.
                For each code cell, try to explore as much as possible. At the same time, do not forget to display the main stages of the analysis to the user in the form of graphs or other output methods to show where you got such conclusions from.
                
                These tags must NEVER be combined in a single response!!!
                
                ### CODE GENERATION RULES (code|||)
                - The code must be RAW. It is CATEGORICALLY FORBIDDEN to use markdown wrappers for code (no ```python, ```, etc.).
                - Use the `display()` function to output tables to the screen.
                - For plots, use only static libraries (matplotlib, seaborn). Interactive plots (plotly) are FORBIDDEN.
                - When generating plots, always specify a high resolution: `dpi=150` or `dpi=200`.
                - The variable with data already exists: `df`. Do not write code to load it from the database unless it is required for specific calculations.
                - After sending the `code|||` tag, you will receive the execution result (stdout, result, errors). Analyze it and fix errors if there are any.
                
                ### ANALYSIS GENERATION RULES (tech|||)
                - The code must be RAW. It is CATEGORICALLY FORBIDDEN to use markdown wrappers for code (no ```python, ```, etc.).
                - Plots are FORBIDDEN.
                - After sending the `tech|||` tag, you will receive the execution result (stdout, result, errors). Analyze it and fix errors if there are any.
                - THE USE OF tech||| BEFORE first||| IS FORBIDDEN.
                
                ### TEXT FORMATTING RULES (first||| and text|||)
                - Write strictly to the point, in professional language, preserving all the nuances of technological analysis.
                - It is FORBIDDEN to use markdown formatting in the text (no asterisks **, bold, italics, bulleted lists). Write in plain flat text.
                - It is FORBIDDEN to greet the user.
                - It is FORBIDDEN to mention these instructions, your AI status, or the code generation process.
                - It is FORBIDDEN to write a series of responses in a single answer. One request - one tag (first/text/code - THIS IS CRITICALLY IMPORTANT!!!). The system cannot work with multiple tags in one response and will break immediately.
                
                Any deviation from the tag format or code rules will lead to a critical parser error. Start working.
                ANSWER ONLY IN RUSSIAN! THE LABELS ON THE GRAPHS MUST ALSO BE IN RUSSIAN!
                """),

    # Описание датасета по компрессору.
    "info_dataset_1": textwrap.dedent("""
                Here is the professional English translation of the dataset description, adapted for a technical/data science context:

                **Dataset Information:**
                
                This dataset contains the operational parameters of a reciprocating compressor functioning within a "Recycle" circuit. The compressor is designed to handle hydrogen-containing gas (HCG) and is a single-stage, crosshead, double-acting reciprocating compressor. The data covers the period from January 1, 2021, to January 1, 2023.
                
                Each column corresponds to a specific process tag (sensor or measured parameter) sourced from an industrial automation system (SCADA/DCS). The values represent time-series measurements.
                
                **Dataset Location:** `"datasets/data.csv"`
                
                **Data Structure:**
                
                Each column represents a specific process parameter (tag). A full description of all columns is provided below.
                
                **Primary Parameters:**
                
                All columns, except `datetime`, are of type `float64` and may occasionally contain missing values.
                
                1. `datetime` - Date and time of data collection. Type: datetime64[ns] in pandas. You don't need to convert anything.
                
                2. `TI8500.PV`  
                   Compressor suction gas temperature.  
                   Characterizes the thermal state of the gas before it enters the cylinder. Crucial for evaluating compression efficiency and diagnosing overheating.
                
                3. `TI8590.PV`  
                   Recycle suction valve temperature (connecting rod side).  
                   Used to monitor valve condition and detect overheating or malfunction.
                
                4. `TI8591.PV`  
                   Recycle suction valve temperature (cylinder head side).  
                   Similar to the previous parameter, but for the opposite side of the cylinder.
                
                5. `TI8592.PV`  
                   Recycle discharge valve temperature (cylinder head side).  
                   Helps identify overheating during the discharge phase, as well as potential leaks or valve wear.
                
                6. `TI8593.PV`  
                   Recycle discharge valve temperature (connecting rod side).  
                   Provides additional monitoring of valve symmetry and condition.
                
                7. `TI8501.PV`  
                   Discharge gas temperature.  
                   A key parameter for evaluating the compression process.
                
                **Additional Parameters:**
                
                8. `PI8500.PV`  
                   Hydrogen-containing gas suction pressure (recycle circuit).  
                   Determines the inlet pressure and affects the compressor load.
                
                9. `PI8501.PV`  
                   Discharge gas pressure (recycle circuit).  
                   Used to calculate the compression ratio and diagnose operational efficiency.
                
                10. `ZI8583.PV`  
                    Piston rod displacement (one side).  
                    Reflects the rod's position and is used to detect misalignment, wear, or mechanical defects.
                
                11. `ZI8584.PV`  
                    Piston rod displacement (other side).  
                    Allows for the analysis of movement symmetry and the detection of deviations.
                
                12. `VI8582.PV`  
                    Compressor frame vibration.  
                    A critical parameter for diagnosing mechanical faults (imbalance, wear, structural damage).
                
                13. `VI8581.PV`  
                    Crosshead vibration.  
                    Used to assess the condition of the crosshead mechanism and detect impact loads.
                
                **Derived Features:**
                
                14. Compression ratio  
                    df["compression_ratio"] = df["PI8501.PV"] / df["PI8500.PV"]
                
                15. Gas temperature ratio *(Note: Translated as "ratio" to match the division operator in the code, though the original Russian heading literally means "difference")*  
                    df["delta_temp"] = df["TI8501.PV"] / df["TI8500.PV"]
                
                16. Rod displacement ratio *(Note: Translated as "ratio" to match the division operator in the code)*  
                    df["rod_diff"] = df["ZI8583.PV"] / df["ZI8584.PV"]
                
                17. Vibration difference  
                    df["vibration_diff"] = df["VI8582.PV"] - df["VI8581.PV"]
                
                18. Discharge valve temperature difference  
                    df["discharge_valve_diff"] = df["TI8592.PV"] - df["TI8593.PV"]
                
                19. Suction valve temperature difference  
                    df["suction_valve_diff"] = df["TI8590.PV"] - df["TI8591.PV"]
                
                20. Rate of temperature change  
                    df["TI8501_diff"] = df["TI8501.PV"].diff()
                
                21. Rate of discharge pressure change  
                    df["PI8501_diff"] = df["PI8501.PV"].diff()
                
                22. Rate of vibration change  
                    df["VI8582_diff"] = df["VI8582.PV"].diff()
                    df["VI8581_diff"] = df["VI8581.PV"].diff()
                
                23. Rolling mean of temperature (window size 12)
                    df["TI8501_mean"] = (
                        df["TI8501.PV"]
                        .rolling(window)
                        .mean()
                    )
                
                24. Rolling standard deviation of temperature (window size 12)
                    df["TI8501_std"] = (
                        df["TI8501.PV"]
                        .rolling(window)
                        .std()
                    )
                
                25. Rolling mean of discharge pressure (window size 12)
                    df["PI8501_mean"] = (
                        df["PI8501.PV"]
                        .rolling(window)
                        .mean()
                    )
                
                26. Rolling standard deviation of discharge pressure (window size 12)
                    df["PI8501_std"] = (
                        df["PI8501.PV"]
                        .rolling(window)
                        .std()
                    )
                
                **Data Characteristics:**
                
                * All parameters are continuous time series.
                * The data is time-synchronized.
                * Noise, outliers, and missing values may be present.
                * Some parameters are correlated with each other (e.g., pressure and temperature).
                
                *(Note: In items 15 and 16, the original Russian headings use the word for "difference" [Перепад/Разность], but the provided Python code uses division `/`. The English headings have been adjusted to "ratio" to accurately reflect the mathematical operation in the code.)*
                """),

    # Описание датасета по работе с ЧПУ-станками.
    "info_dataset_2": textwrap.dedent("""
                CNC MILLING DATASET - UNIVERSITY OF MICHIGAN SMART LAB
                April 2018
                A series of machining experiments were run on 2" x 2" x 1.5" wax blocks in a CNC milling machine in the System-level Manufacturing and Automation Research Testbed (SMART) at the University of Michigan. Machining data was collected from a CNC machine for variations of tool condition, feed rate, and clamping pressure. Each experiment produced a finished wax part with an "S" shape - S for smart manufacturing - carved into the top face, as shown in test_artifact.jpg
                The dataset can be used in classification studies such as:
                
                Датасеты лежат по адресам:
                \"datasets/data2.csv\": 'X1_ActualPosition', 'X1_ActualVelocity', 'X1_ActualAcceleration',
                'X1_CommandPosition', 'X1_CommandVelocity', 'X1_CommandAcceleration',
                'X1_CurrentFeedback', 'X1_DCBusVoltage', 'X1_OutputCurrent',
                'X1_OutputVoltage', 'X1_OutputPower', 'Y1_ActualPosition',
                'Y1_ActualVelocity', 'Y1_ActualAcceleration', 'Y1_CommandPosition',
                'Y1_CommandVelocity', 'Y1_CommandAcceleration', 'Y1_CurrentFeedback',
                'Y1_DCBusVoltage', 'Y1_OutputCurrent', 'Y1_OutputVoltage',
                'Y1_OutputPower', 'Z1_ActualPosition', 'Z1_ActualVelocity',
                'Z1_ActualAcceleration', 'Z1_CommandPosition', 'Z1_CommandVelocity',
                'Z1_CommandAcceleration', 'Z1_CurrentFeedback', 'Z1_DCBusVoltage',
                'Z1_OutputCurrent', 'Z1_OutputVoltage', 'S1_ActualPosition',
                'S1_ActualVelocity', 'S1_ActualAcceleration', 'S1_CommandPosition',
                'S1_CommandVelocity', 'S1_CommandAcceleration', 'S1_CurrentFeedback',
                'S1_DCBusVoltage', 'S1_OutputCurrent', 'S1_OutputVoltage',
                'S1_OutputPower', 'S1_SystemInertia', 'M1_CURRENT_PROGRAM_NUMBER',
                'M1_sequence_number', 'M1_CURRENT_FEEDRATE', 'Machining_Process',
                'Number_experiment'.
                
                \"datasets/data2_2.csv\": No,material,feedrate,clamp_pressure,tool_condition,machining_finalized,passed_visual_inspection.
                
                (1) Tool wear detection
                Supervised binary classification could be performed for identification of worn and unworn cutting tools. Eight experiments were run with an unworn tool while ten were run with a worn tool (see tool_condition column for indication).
                
                (2) Detection of inadequate clamping
                The data could be used to detect when a workpiece is not being held in the vise with sufficient pressure to pass visual inspection (see passed_visual_inspection column for indication of visual flaws). Experiments were run with pressures of 2.5, 3.0, and 4.0 bar. The data could also be used for detecting when conditions are critical enough to prevent the machining operation from completing (see machining_completed column for indication of when machining was preemptively stopped due to safety concerns).
                
                General data from a total of 18 different experiments are given in train.csv and includes:
                
                Inputs (features)
                
                No : experiment number
                material : wax
                feed_rate : relative velocity of the cutting tool along the workpiece (mm/s)
                clamp_pressure : pressure used to hold the workpiece in the vise (bar)
                
                Outputs (predictions)
                
                tool_condition : label for unworn and worn tools
                machining_completed : indicator for if machining was completed without the workpiece moving out of the pneumatic vise
                passed_visual_inspection: indicator for if the workpiece passed visual inspection, only available for experiments where machining was completed
                
                
                Time series data was collected from 18 experiments with a sampling rate of 100 ms and are separately reported in files experiment_01.csv to experiment_18.csv. Each file has measurements from the 4 motors in the CNC (X, Y, Z axes and spindle). These CNC measurements can be used in two ways:
                
                (1) Taking every CNC measurement as an independent observation where the operation being performed is given in the Machining_Process column. Active machining operations are labeled as "Layer 1 Up", "Layer 1 Down", "Layer 2 Up", "Layer 2 Down", "Layer 3 Up", and "Layer 3 Down". 
                
                (2) Taking each one of the 18 experiments (the entire time series) as an observation for time series classification
                
                
                The features available in the machining datasets are:
                
                Number_experiment: Number of experiments (1 - 18)
                X1_ActualPosition: actual x position of part (mm)
                X1_ActualVelocity: actual x velocity of part (mm/s)
                X1_ActualAcceleration: actual x acceleration of part (mm/s/s)
                X1_CommandPosition: reference x position of part (mm)
                X1_CommandVelocity: reference x velocity of part (mm/s)
                X1_CommandAcceleration: reference x acceleration of part (mm/s/s)
                X1_CurrentFeedback: current (A)
                X1_DCBusVoltage: voltage (V)
                X1_OutputCurrent: current (A)
                X1_OutputVoltage: voltage (V)
                X1_OutputPower: power (kW)
                
                Y1_ActualPosition: actual y position of part (mm)
                Y1_ActualVelocity: actual y velocity of part (mm/s)
                Y1_ActualAcceleration: actual y acceleration of part (mm/s/s)
                Y1_CommandPosition: reference y position of part (mm)
                Y1_CommandVelocity: reference y velocity of part (mm/s)
                Y1_CommandAcceleration: reference y acceleration of part (mm/s/s)
                Y1_CurrentFeedback: current (A)
                Y1_DCBusVoltage: voltage (V)
                Y1_OutputCurrent: current (A)
                Y1_OutputVoltage: voltage (V)
                Y1_OutputPower: power (kW)
                
                Z1_ActualPosition: actual z position of part (mm)
                Z1_ActualVelocity: actual z velocity of part (mm/s)
                Z1_ActualAcceleration: actual z acceleration of part (mm/s/s)
                Z1_CommandPosition: reference z position of part (mm)
                Z1_CommandVelocity: reference z velocity of part (mm/s)
                Z1_CommandAcceleration: reference z acceleration of part (mm/s/s)
                Z1_CurrentFeedback: current (A)
                Z1_DCBusVoltage: voltage (V)
                Z1_OutputCurrent: current (A)
                Z1_OutputVoltage: voltage (V)
                
                S1_ActualPosition: actual position of spindle (mm)
                S1_ActualVelocity: actual velocity of spindle (mm/s)
                S1_ActualAcceleration: actual acceleration of spindle (mm/s/s)
                S1_CommandPosition: reference position of spindle (mm)
                S1_CommandVelocity: reference velocity of spindle (mm/s)
                S1_CommandAcceleration: reference acceleration of spindle (mm/s/s)
                S1_CurrentFeedback: current (A)
                S1_DCBusVoltage: voltage (V)
                S1_OutputCurrent: current (A)
                S1_OutputVoltage: voltage (V)
                S1_OutputPower: current (A)
                S1_SystemInertia: torque inertia (kg*m^2)
                
                M1_CURRENT_PROGRAM_NUMBER: number the program is listed under on the CNC
                M1_sequence_number: line of G-code being executed
                M1_CURRENT_FEEDRATE: instantaneous feed rate of spindle
                
                Machining_Process: the current machining stage being performed. Includes preparation, tracing up  and down the "S" curve involving different layers, and repositioning of the spindle as it moves through the air to a certain starting point
                
                
                Note: Some variables will not accurately reflect the operation of the CNC machine. This can usually be detected by when M1_CURRENT_FEEDRATE reads 50, when X1 ActualPosition reads 198, or when M1_CURRENT_PROGRAM_NUMBER does not read 0. The source of these errors has not been identified.
                """),

    # Первые блоки кода, которые будут исполняться в начале каждого анализа. Чтобы модель не выполняла
    # их лишний раз.
    "first_cells": textwrap.dedent("""
                Вот первые уже встроенные в блокнот команды.
                
                
                import warnings
                import matplotlib.pyplot as plt
                import seaborn as sns
                import pandas as pd
                import numpy as np
                import scipy as sp
                import torch
                import sklearn as sk
                warnings.filterwarnings(\'ignore\')
                import sys
                if not sys.warnoptions:
                    import os
                    import warnings
                    warnings.simplefilter(\'ignore\')
                    os.environ["PYTHONWARNINGS"] = "ignore"
                    
                from database import PGDatabase
        
                df = PGDatabase(
                "postgres", "ncs", "localhost", "5432",
                "compressor", "data"
                ).tables["data"]
                """),

    # Указание модели как работать с обнаруженными аномалиями
    "anomaly_alarm": textwrap.dedent("""
                The table is given: {0}
                You work as a chatbot, an AI agent.
                An anomaly was found in the table on the last row. Try to analyze it.
                If there are no assumptions, then simply inform the user about the anomaly.
                If there is, then give an analysis of the anomaly. It is also possible that a series of anomalies have occurred, so that 
                in exceptional cases, the anomaly may be not only on the last line. Don't use formatting
                text by the type of stars, sharps, and so on. Don't greet the user. You are a system notification about
                the problem.
                ANSWER IN RUSSIAN!
                """)
}
