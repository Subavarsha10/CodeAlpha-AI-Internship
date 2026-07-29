const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const translateRoutes = require("./routes/translate"); // Corrected file name here!

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use("/api", translateRoutes);

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});