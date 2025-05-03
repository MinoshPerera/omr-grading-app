# MarkIt™ - The Premium OMR Solution for Modern Educators

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your_streamlit_app_url)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-%23white.svg?logo=opencv&logoColor=black)](https://opencv.org/)
[![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?logo=numpy&logoColor=white)](https://numpy.org/)
[![Pillow](https://img.shields.io/badge/Pillow-FFD43B?logo=Pillow&logoColor=blue)](https://pillow.readthedocs.io/en/stable/)
[![XLSXWriter](https://img.shields.io/badge/XLSXWriter-%23214932.svg?logo=&logoColor=white)](https://xlsxwriter.readthedocs.io/)

**MarkIt™** is a cutting-edge Optical Mark Recognition (OMR) solution designed to help educators grade multiple-choice exams with unparalleled speed and accuracy. Leveraging advanced image processing techniques, MarkIt™ transforms the tedious task of manual grading into a swift and efficient process.

## 🚀 Key Features

* **⚡ Blazing Fast Processing:** Grade answer sheets in mere seconds, saving valuable time for educators.
* **🎯 High Accuracy:** Employs sophisticated image processing for precise detection of marked bubbles, minimizing errors.
* **📊 Comprehensive Analytics:** Provides detailed reports and insightful analytics on student performance.
* **🔑 Flexible Answer Key Configuration:** Easily set up answer keys manually or by importing from a CSV file.
* **📤 CSV Import/Export:** Streamline the process by importing answer keys and exporting detailed results in CSV/Excel format.
* **🔒 Privacy Focused:** All processing is done locally within your session, ensuring the privacy of your data.
* **✨ Premium User Interface:** A clean, intuitive, and professional interface powered by Streamlit for a seamless user experience.
* **🖼️ Marked Answer Sheet Visualization:** See the graded answer sheet with correct and incorrect answers clearly marked.
* **📉 Performance Insights:** Visualize student performance with charts and detailed question analysis.

## 🛠️ Installation

No installation is required! This application runs directly in your web browser using Streamlit. Simply upload the Python script (`OMR_grading_tool.py`) to a Streamlit sharing platform or run it locally if you have Streamlit installed.

### Running Locally (if needed)

1.  Make sure you have Python and Streamlit installed. If not, you can install them using pip:
    ```bash
    pip install streamlit opencv-python numpy pandas pillow openpyxl xlsxwriter
    ```
2.  Save the provided Python code as `OMR_grading_tool.py`.
3.  Navigate to the directory where you saved the file in your terminal.
4.  Run the Streamlit app:
    ```bash
    streamlit run OMR_grading_tool.py
    ```
5.  The application will automatically open in your web browser.

## ⚙️ Usage

MarkIt™ is designed with a user-friendly tab-based interface for a straightforward workflow:

### 1. 🔑 Configure Answer Key

* **Manual Configuration:** Set the correct answer (1-5) for each of the 50 questions using the interactive select boxes.
* **CSV Import:** Upload a CSV file with two columns: "Question" (number from 1 to 50) and "Answer" (correct option number from 1 to 5). A sample CSV file format is provided for download.
* Click the "💾 Save Answer Key" button to store your configured key.

### 2. 📝 Grade Answer Sheets

* **Student Information (Optional):** Enter the student's name and ID for better result tracking.
* **Upload Answer Sheet:** Click on "📤 Upload a scanned answer sheet image" to upload images in JPG, PNG, or JPEG format. Ensure the image is clear and well-lit for optimal processing.
* Once uploaded, the application will automatically process the image and display the results, including the score, percentage, a marked answer sheet, and a detailed question-wise analysis.
* **Download Results:** You can download the detailed results as an Excel file and the marked answer sheet as a PNG image.

### 3. 📊 Analytics Dashboard

* This tab provides a summary of all the answer sheets processed during the current session.
* View the total number of processed sheets, average score, and highest score.
* A table displays the results of each processed sheet.
* An option to "📥 Export All Results" allows you to download a comprehensive Excel file of all processed data.

## 🤝 Contributing

Contributions to enhance MarkIt™ are welcome! Feel free to fork the repository, make improvements, and submit a pull request.

## 📜 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## 🙏 Acknowledgements

* Built with ❤️ using [Streamlit](https://streamlit.io/).
* Leverages the power of [OpenCV](https://opencv.org/) for image processing, [NumPy](https://numpy.org/) for numerical operations, [Pandas](https://pandas.pydata.org/) for data manipulation, and [Pillow](https://pillow.readthedocs.io/en/stable/) for image handling.
* Utilizes [XLSXWriter](https://xlsxwriter.readthedocs.io/) for creating Excel reports.
* Styled with custom CSS to provide a premium user experience.

---

**MarkIt™ - Bringing Speed and Accuracy to Exam Grading**
