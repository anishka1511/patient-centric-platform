import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Randomization helper functions
function getRandomExperience() {
  return Math.floor(Math.random() * 29) + 2; // 2-30 years
}

function getRandomRating() {
  const ratings = [65, 72, 78, 82, 85, 88, 90, 92, 94, 96, 98];
  return ratings[Math.floor(Math.random() * ratings.length)]; // Return just the number
}

function getRandomAvailability() {
  const availabilities = ['Available Today', 'Schedule Appointment'];
  return availabilities[Math.floor(Math.random() * availabilities.length)];
}

function getRandomCost(baseCost) {
  // Randomize cost by ±10-20%
  const variation = 0.85 + Math.random() * 0.35; // 0.85 to 1.2
  const numMatch = baseCost.match(/\d+/);
  if (numMatch) {
    const baseNum = parseInt(numMatch[0]);
    const randomCost = Math.round(baseNum * variation / 50) * 50; // Round to nearest 50
    return `₹${randomCost}`;
  }
  return baseCost;
}

// Read all specialty JSON files
const mockDir = path.join(__dirname, '../src/mock');
const files = fs.readdirSync(mockDir).filter(f => f.endsWith('.json'));

console.log(`📂 Processing ${files.length} specialty files...`);

files.forEach(file => {
  const filePath = path.join(mockDir, file);
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

  // Process each hospital
  data.hospitals.forEach(hospital => {
    // Process each doctor
    hospital.doctors.forEach(doctor => {
      // Randomize experience
      doctor.experience_years = getRandomExperience();

      // Randomize availability (but prioritize 50% available today for better UX)
      if (Math.random() > 0.4) {
        doctor.availability = 'Available Today';
      } else {
        doctor.availability = 'Schedule Appointment';
      }

      // Randomize rating (store as numeric value only, no percentage)
      doctor.rating = getRandomRating();

      // Clean up cost (fix Unicode rupee symbol)
      doctor.cost = getRandomCost(doctor.cost);

      // Ensure clean string values
      doctor.location = String(doctor.location).trim();
      doctor.phone = String(doctor.phone).trim();
    });
  });

  // Write back the cleaned and randomized data
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
  console.log(`✅ ${file} updated`);
});

console.log('\n🎉 All doctor data cleaned and randomized!');
