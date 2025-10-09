# SEFAZ Query Automator

A modern and automated system with a web interface to query and request XML files from the SEFAZ (Secretaria da Fazenda) portal. This tool is designed to optimize the routine of accounting and tax professionals.

**TODO:** Replace this with a screenshot or GIF of your project!
![Project Screenshot](https://via.placeholder.com/800x400.png?text=Your+Project+Screenshot)

[**Live Demo (Coming Soon)**](https://your-live-demo-link.com) <!-- TODO: Replace with your live demo link after deploying -->

---

## 🚀 Case Study: Automating Tax Document Retrieval

### The Challenge

Accountants and tax professionals often need to download a large volume of XML files (NFe, NFCe, CTe) from government portals like SEFAZ. This manual process is extremely time-consuming, repetitive, and prone to human error, consuming hours of work that could be better spent on analysis and consulting.

### The Solution

The SEFAZ Query Automator was developed to solve this problem. It's a Python-based application with a user-friendly web interface built with Streamlit. The application automates the entire process of logging into the SEFAZ portal, filling out the query forms, and requesting the XML files in bulk based on a simple spreadsheet input.

The system is built with resilience and user experience in mind, featuring:

*   **Session and Checkpoint System:** The application saves the progress of a batch process. If the browser crashes or the connection is lost, the user can resume from where they left off.
*   **Real-time Logs:** A detailed log provides full visibility into the automation process, showing the status of each request.
*   **Secure Credential Management:** Uses a `.env` file to store sensitive credentials, keeping them out of the source code.

### The Impact

*   **Drastic Time Reduction:** Automated a process that took hours, reducing it to minutes.
*   **Increased Accuracy:** Eliminated errors associated with manual data entry.
*   **Improved Workflow:** Freed up professionals to focus on higher-value tasks.

---

## ✨ Key Features

*   **Web Interface:** A clean and modern UI built with Streamlit.
*   **Bulk Processing:** Process hundreds of requests from a single Excel spreadsheet.
*   **Resilient Automation:** Handles login, navigation, and form submission automatically.
*   **Session Persistence:** Saves uploaded spreadsheets and progress.
*   **Headless Mode:** Option to run the browser in the background for better performance.

---

## 🛠️ Technologies Used

*   **Backend:** Python
*   **Web Framework:** Streamlit
*   **Browser Automation:** Selenium
*   **Libraries:** Pandas, OpenPyXL, python-decouple

---

## 📦 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AdrianHaelisson/sefaz-query-automator.git
    cd sefaz-query-automator
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure your credentials:**
    *   Copy the `env.example` file to a new file named `.env`.
    *   Open the `.env` file and fill in your `SEFAZ_USUARIO` and `SEFAZ_SENHA`.

4.  **Run the application:**
    ```bash
    python run.py
    ```

5.  Open your browser and navigate to `http://localhost:8501`.

---

## 🚀 How to Deploy

This application can be deployed for free on [Streamlit Community Cloud](https://streamlit.io/cloud).

1.  **Push your code to a public GitHub repository.**
2.  Sign up for Streamlit Cloud and connect your GitHub account.
3.  Click "New app" and select the repository.
4.  In the "Advanced settings", you will need to add your `SEFAZ_USUARIO` and `SEFAZ_SENHA` as secrets.
5.  Click "Deploy!"

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
