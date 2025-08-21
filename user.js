const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  username: String,
  email: String,
  fullName: String,
  password: String, // Securely store hashed password
  travelPreferences: String,
  travelDestination: String,
  travelStartDate: Date,
  travelEndDate: Date,
  gender: String
});

module.exports = mongoose.model('User', userSchema);