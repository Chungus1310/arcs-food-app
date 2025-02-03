# 🍽️ F&B Management System

A sleek and modern Flask-based Food & Beverage Management System designed to help restaurants manage their operations efficiently.

## 🌟 Features

- 👥 Customer Management
	- Add, edit, and view customer information
	- Track customer orders and preferences

- 🛒 Order Management
	- Create and process orders
	- Track order history
	- Search orders with advanced filters

- 🍜 Menu Management
	- Manage menu items and prices
	- Easy menu updates

- 📊 Advanced Reporting
	- Customer order statistics
	- Revenue tracking
	- Popular item combinations
	- Custom queries and analytics

## 🚀 Quick Start

1. Clone the repository:
	 ```bash
	 git clone https://github.com/Chungus1310/arcs-food-app.git
	 cd arcs-food-app
	 ```

2. Create and activate virtual environment:
	 ```bash
	 python -m venv venv
	 source venv/bin/activate  # On Windows: venv\Scripts\activate
	 ```

3. Install dependencies:
	 ```bash
	 pip install -r requirements.txt
	 ```

4. Run the application:
	 ```bash
	 python app.py
	 ```

5. Visit `http://localhost:5000` in your browser

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Bootstrap 5, Custom CSS
- **Database**: SQLite (development)
- **Icons**: Bootstrap Icons

## 📁 Project Structure

```
flask_food_app/
│
├── app.py                 # Main application file
├── config.py             # Configuration settings
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── static/              # Static files
│   ├── images/         # Images including bg.png
│   ├── styles.css      # Custom CSS
│   └── scripts.js      # Custom JavaScript
│
└── templates/           # HTML templates
		├── base.html       # Base template
		├── index.html      # Home page
		└── ...            # Other template files
```

## 🎨 Customization

- Background image can be changed by replacing `static/images/bg.png`
- Theme colors can be modified in `static/styles.css`
- Custom JavaScript functionality in `static/scripts.js`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- Bootstrap for the awesome UI components
- Flask community for the excellent documentation
- All contributors who help improve this project

---
Made with ❤️ by [Chun]

