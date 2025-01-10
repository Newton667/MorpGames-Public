const express = require('express');
const mongoose = require('mongoose');
const path = require('path');
const cors = require('cors'); // Importing CORS middleware
const app = express();
const ejs = require('ejs');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');
const crypto = require('crypto'); // For generating random passwords
const session = require('express-session');
const nodemailer = require('nodemailer');
const stringSimilarity = require('string-similarity');
const sharp = require('sharp'); // For resizing images

// Middleware for CORS
app.use(cors({
    origin: ':)', // Replace with your frontend's URL
    credentials: true // Allow cookies and credentials
}));

// Middleware for static files
app.use(express.static(path.join(__dirname, 'public'))); // Serve files from the `morpGames` directory


// Middleware for parsing requests
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' })); // Increase limit to 10MB
app.use(bodyParser.json({ limit: '10mb' })); // Increase limit to 10MB


// Middleware for parsing requests
app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Session middleware
app.use(session({
    secret: 'defaultsecret', // Use a secure secret
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: false, // Set to `true` if using HTTPS
        httpOnly: true,
        sameSite: 'Lax', // Required for cross-domain cookies
    },
}));

// MongoDB Connection
mongoose.connect('API HERE', {
    useNewUrlParser: true,
    useUnifiedTopology: true
})
    .then(() => {
        console.log('Connected successfully to MongoDB.');
    })
    .catch(err => {
        console.error('Error connecting to MongoDB:', err);
    });

// Root route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'Main.html'));
});



// Schemas
const leaderboardSchema = new mongoose.Schema({
    username: { type: String, required: true },
    score: { type: Number, required: true },
    proof: { type: String, required: true }, // Path or URL to the proof image
    timestamp: { type: Date, default: Date.now }
});

const forumnSchema = {
    name: String,
    comment: String
};

const accountSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    gold: { type: Number, default: 100 },
    scores: { type: Array, default: [] },
    profileImage: { type: String, default: 'default-profile.png' }, // Path or URL to the current profile image
    profilePictureInventory: { type: [String], default: [] } // Array of image paths or URLs
});

function getChannelModel(channel) {
    if (mongoose.models[channel]) {
        return mongoose.models[channel];
    }

    const schema = new mongoose.Schema({
        channel: { type: String, required: true },
        username: { type: String, required: true },
        profileImage: { type: String, required: true },
        message: { type: String, default: '' }, // Message is optional if an image is sent
        image: { type: String, default: null }, // Base64 string or file path
        timestamp: { type: Date, default: Date.now },
    });

    return mongoose.model(channel, schema, `Morpcord.${channel}`);
}






// Models for each game
const MorpRougeLeaderboard = mongoose.model('MorpRougeLeaderboard', leaderboardSchema, 'MorpRougeLeaderboard');
const MorphouLeaderboard = mongoose.model('MorphouLeaderboard', leaderboardSchema, 'MorphouLeaderboard');
const EvilMorpLeaderboard = mongoose.model('EvilMorpLeaderboard', leaderboardSchema, 'EvilMorpLeaderboard');
const SudokuLeaderboard = mongoose.model('SudokuLeaderboard', leaderboardSchema, 'SudokuLeaderboard');
const SlidingTileLeaderboard = mongoose.model('SlidingTileLeaderboard', leaderboardSchema, 'SlidingTileLeaderboard');

// Models for each game using the corrected schema name
const Score1 = mongoose.model('TimScores', leaderboardSchema, 'TimScores');
const Score2 = mongoose.model('NewtonScores', leaderboardSchema, 'NewtonScores');
const Score3 = mongoose.model('GabeScores', leaderboardSchema, 'GabeScores');
const Score4 = mongoose.model('JesseScores', leaderboardSchema, 'JesseScores');
const Score5 = mongoose.model('NatalyScores', leaderboardSchema, 'NatalyScores');




const Accounts = mongoose.model('Accounts', accountSchema, 'Accounts');

// Routes
app.get('/leaderboards', async (req, res) => {
    try {
        const timScores = await Score1.find({}).sort({ score: -1 }).limit(5);
        const newtonScores = await Score2.find({}).sort({ score: -1 }).limit(5);
        const gabeScores = await Score3.find({}).sort({ score: -1 }).limit(5);
        const jesseScores = await Score4.find({}).sort({ score: -1 }).limit(5);
        const natalyScores = await Score5.find({}).sort({ score: -1 }).limit(5);

        res.render('leaderboards', {
            timScores,
            newtonScores,
            gabeScores,
            jesseScores,
            natalyScores,
        });
    } catch (err) {
        console.error('Error fetching leaderboards:', err.message);
        res.status(500).send('Failed to fetch leaderboards.');
    }
});




app.get('/forum', async (req, res) => {
    try {
        const morphouF = await morphouForum.find({}).sort({ _id: -1 }).limit(5);
        const rogueF = await rogueForum.find({}).sort({ _id: -1 }).limit(5);
        const sudokuF = await sudokuForum.find({}).sort({ _id: -1 }).limit(5);
        const sliderF = await sliderForum.find({}).sort({ _id: -1 }).limit(5);
        const platformerF = await platformerForum.find({}).sort({ _id: -1 }).limit(5);

        res.render('forum', { morphouF, rogueF, sudokuF, sliderF, platformerF });
    } catch (err) {
        console.error(err);
        res.status(500).send('Server Error');
    }
});

app.post('/post-comment', async (req, res) => {
    try {
        const { game, name, comment } = req.body;

        let forumModel;
        switch (game) {
            case 'morphouF':
                forumModel = morphouForum;
                break;
            case 'rougeF':
                forumModel = rogueForum;
                break;
            case 'sudokuF':
                forumModel = sudokuForum;
                break;
            case 'sliderF':
                forumModel = sliderForum;
                break;
            case 'platformerF':
                forumModel = platformerForum;
                break;
            default:
                return res.status(400).send('Invalid game selected');
        }

        const newComment = new forumModel({ name, comment });
        await newComment.save();
        res.redirect('/forum');
    } catch (err) {
        console.error(err);
        res.status(500).send('Server Error');
    }
});

app.get('/signup.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'Signup.html'));
});

app.post('/signup', async (req, res) => {
    try {
        const { username, email, password } = req.body;

        // Check if username or email already exists
        const existingUser = await Accounts.findOne({ $or: [{ username }, { email }] });
        if (existingUser) {
            return res.status(400).json({ error: 'Username or email already taken' });
        }

        // Hash password before saving
        const hashedPassword = await bcrypt.hash(password, 10);

        // Create new account with a default profile picture and inventory
        const newAccount = new Accounts({
            username,
            email,
            password: hashedPassword,
            profileImage: 'shopimg/Morp_2.png', // Set default profile image
            profilePictureInventory: ['shopimg/Morp_2.png'], // Give free skin
        });
        await newAccount.save();

        res.status(201).json({ message: 'Signup successful!' });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error during signup' });
    }
});


// Login route
app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    const user = await Accounts.findOne({ username });
    if (user && (await bcrypt.compare(password, user.password))) {
        req.session.username = username; // Set the session
        console.log('Session set:', req.session); // Debugging: Log the session
        res.json({ message: 'Login successful' });
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
});


// Endpoint to get the logged-in username
app.get('/user', async (req, res) => {
    if (req.session && req.session.username) {
        try {
            const user = await Accounts.findOne({ username: req.session.username });

            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }

            res.json({
                username: user.username,
                gold: user.gold,
                profilePictureInventory: user.profilePictureInventory, // Include inventory
            });
        } catch (error) {
            console.error('Error fetching user data:', error);
            res.status(500).json({ error: 'Failed to fetch user data.' });
        }
    } else {
        res.status(401).json({ error: 'User not logged in.' });
    }
});



app.get('/account', async (req, res) => {
    console.log('Session data:', req.session); // Debugging: Check session

    if (req.session && req.session.username) {
        try {
            const user = await Accounts.findOne({ username: req.session.username });
            console.log('Fetched user:', user); // Debugging: Check user data

            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }

            res.json({
                username: user.username,
                email: user.email, // Ensure email is included if needed
                profileImage: user.profileImage || 'img/default-profile.png',
                gold: user.gold || 0,
                profilePictureInventory: user.profilePictureInventory || []
            });
        } catch (error) {
            console.error('Error fetching user details:', error);
            res.status(500).json({ error: 'Failed to fetch account details' });
        }
    } else {
        res.status(401).json({ error: 'User not logged in.' });
    }
});





// Logout route
app.post('/logout', (req, res) => {
    if (req.session) {
        // Destroy the session
        req.session.destroy((err) => {
            if (err) {
                console.error('Error destroying session:', err);
                res.status(500).json({ error: 'Failed to log out' });
            } else {
                res.clearCookie('connect.sid'); // Clear the session cookie
                res.json({ message: 'Logout successful' });
            }
        });
    } else {
        res.status(400).json({ error: 'No session to log out' });
    }
});
// Forget Password route
app.post('/forgot-password', async (req, res) => {
    const { username, email } = req.body;

    try {
        // Find the user by email
        const user = await Accounts.findOne({ email });

        if (!user) {
            return res.status(404).json({ error: 'No account found with this email.' });
        }

        // Check if the provided username is close enough to the actual username
        const similarity = (str1, str2) => {
            let matches = 0;
            for (let i = 0; i < Math.min(str1.length, str2.length); i++) {
                if (str1[i].toLowerCase() === str2[i].toLowerCase()) matches++;
            }
            return matches / Math.max(str1.length, str2.length);
        };

        if (similarity(username, user.username) < 0.5) {
            return res.status(400).json({ error: 'Provided username does not match our records.' });
        }

        // Generate a new random password
        const newPassword = crypto.randomBytes(8).toString('hex');

        // Hash the new password
        const hashedPassword = await bcrypt.hash(newPassword, 10);

        // Update the password in the database
        user.password = hashedPassword;
        await user.save();

        // Set up the nodemailer transporter
        const transporter = nodemailer.createTransport({
            service: 'gmail',
            auth: {
                user: process.env.EMAIL_USER,
                pass: process.env.EMAIL_PASS,
            },
        });

        // Send the email with embedded image and fancy HTML
        const mailOptions = {
            from: '"Morp Games Support" <morpgames420@gmail.com>',
            to: email,
            subject: 'Password Reset - Morp Games',
            html: `
                <div style="font-family: Arial, sans-serif; color: #333; background-color: #f4f4f9; padding: 20px; border-radius: 10px; max-width: 600px; margin: 20px auto; text-align: center; border: 2px solid #00FF99;">
                    <h1 style="color: #00FF99; text-shadow: 0 0 5px #FF66CC;">Morp Games Password Reset</h1>
                    <p style="font-size: 16px; color: #555;">Hello <strong>${user.username}</strong>,</p>
                    <p style="font-size: 16px; color: #555;">Your password has been reset. Please use the new password below to log in:</p>
                    <div style="background-color: #222; color: #00FF99; padding: 15px; margin: 20px auto; font-size: 18px; border-radius: 5px; display: inline-block;">
                        <strong>${newPassword}</strong>
                    </div>
                    <p style="font-size: 16px; color: #555;">We recommend changing your password after logging in.</p>
                    <img src="cid:bigmorp@morpgames" alt="Morp" style="width: 200px; margin: 20px auto; display: block;">
                    <p style="font-size: 14px; color: #aaa;">If you did not request this password reset, please contact us immediately.</p>
                    <p style="font-size: 16px; color: #555;">Best regards,<br><strong>The Morp Games Team</strong></p>
                </div>
            `,
            attachments: [
                {
                    filename: 'bigmorp.png',
                    path: path.join(__dirname, 'public', 'img', 'bigmorp.png'), // Path to the image
                    cid: 'bigmorp@morpgames', // Content-ID for embedding
                },
            ],
        };

        await transporter.sendMail(mailOptions);

        res.status(200).json({ message: 'Password reset email sent successfully.' });
    } catch (error) {
        console.error('Error during password reset:', error);
        res.status(500).json({ error: 'An error occurred during password reset.' });
    }
});


// Change Password Route
app.post('/change-password', async (req, res) => {
    const { oldPassword, newPassword } = req.body;

    try {
        // Check if the user is logged in
        if (!req.session || !req.session.username) {
            return res.status(401).json({ error: 'You must be logged in to change your password.' });
        }

        // Find the user in the database
        const user = await Accounts.findOne({ username: req.session.username });

        if (!user) {
            return res.status(404).json({ error: 'User not found.' });
        }

        // Validate the old password
        const isPasswordValid = await bcrypt.compare(oldPassword, user.password);
        if (!isPasswordValid) {
            return res.status(400).json({ error: 'Current password is incorrect.' });
        }

        // Hash the new password
        const hashedPassword = await bcrypt.hash(newPassword, 10);

        // Update the password in the database
        user.password = hashedPassword;
        await user.save();

        res.status(200).json({ message: 'Password changed successfully.' });
    } catch (error) {
        console.error('Error during password change:', error);
        res.status(500).json({ error: 'An error occurred while changing the password.' });
    }
});


app.post('/delete-account', async (req, res) => {
    try {
        const { username } = req.body;

        // Validate session and ensure the user is logged in
        if (!req.session || !req.session.username) {
            return res.status(401).json({ error: 'User not logged in.' });
        }

        // Ensure the username in the request matches the logged-in user's username
        if (username !== req.session.username) {
            return res.status(403).json({ error: 'Username does not match the logged-in user.' });
        }

        // Delete the user's account from the database
        const result = await Accounts.deleteOne({ username });

        if (result.deletedCount === 0) {
            return res.status(404).json({ error: 'Account not found.' });
        }

        // Destroy the session after deletion
        req.session.destroy((err) => {
            if (err) {
                console.error('Error destroying session:', err);
                return res.status(500).json({ error: 'Failed to destroy session.' });
            }
        });

        res.status(200).json({ message: 'Account successfully deleted.' });
    } catch (error) {
        console.error('Error deleting account:', error);
        res.status(500).json({ error: 'An error occurred while deleting the account.' });
    }
});

app.post('/add-gold', async (req, res) => {
    if (!req.session || !req.session.username) {
        return res.status(401).json({ error: 'User not logged in' });
    }

    try {
        const user = await Accounts.findOne({ username: req.session.username });

        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        user.gold += req.body.amount || 0;
        await user.save();

        res.status(200).json({ message: 'Gold added successfully', gold: user.gold });
    } catch (error) {
        console.error('Error adding gold:', error);
        res.status(500).json({ error: 'An error occurred while adding gold' });
    }
});

app.post('/buy-item', async (req, res) => {
    const { itemName } = req.body;
    
    if (!req.session || !req.session.username) {
        return res.status(401).json({ error: 'User not logged in' });
    }

    try {
        const user = await Accounts.findOne({ username: req.session.username });

        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        if (user.gold < 100) {
            return res.status(400).json({ error: 'Not enough gold' });
        }

        if (!user.profilePictureInventory.includes(`shopimg/${itemName}`)) {
            // Add item to the user's inventory and deduct gold
            user.profilePictureInventory.push(`shopimg/${itemName}`);
            user.gold -= 100;

            await user.save();

            return res.json({
                message: 'Item purchased',
                gold: user.gold,
                profilePictureInventory: user.profilePictureInventory, // Send updated inventory
            });
        } else {
            return res.status(400).json({ error: 'You already own this item' });
        }
    } catch (error) {
        console.error('Error purchasing item:', error);
        res.status(500).json({ error: 'An error occurred while purchasing the item' });
    }
});


app.post('/update-profile-picture', async (req, res) => {
    if (!req.session || !req.session.username) {
        return res.status(401).json({ error: 'User not logged in' });
    }

    const { profileImage } = req.body;
    if (!profileImage) {
        return res.status(400).json({ error: 'No profile image specified' });
    }

    try {
        const user = await Accounts.findOne({ username: req.session.username });

        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        // Update the user's profile picture
        user.profileImage = profileImage;
        await user.save();

        console.log('Profile image updated in database:', user.profileImage); // Debugging log
        res.status(200).json({ message: 'Profile picture updated successfully' });
    } catch (error) {
        console.error('Error updating profile picture:', error);
        res.status(500).json({ error: 'Failed to update profile picture' });
    }
});

app.get('/morpcord/messages/:channel', async (req, res) => {
    const { channel } = req.params;

    if (!channel) {
        return res.status(400).json({ error: 'Channel is required' });
    }

    try {
        const ChannelMessageModel = getChannelModel(channel);
        const messages = await ChannelMessageModel.find({}).sort({ timestamp: 1 });
        res.status(200).json(messages);
    } catch (err) {
        console.error('Error fetching messages:', err);
        res.status(500).json({ error: 'Failed to fetch messages.' });
    }
});



app.post('/morpcord/messages', async (req, res) => {
    const { channel, message, image } = req.body;

    if (!channel || (!message && !image)) {
        return res.status(400).json({ error: 'Channel, message, or image is required.' });
    }

    if (!req.session || !req.session.username) {
        return res.status(401).json({ error: 'User not logged in.' });
    }

    try {
        const user = await Accounts.findOne({ username: req.session.username });

        if (!user) {
            return res.status(404).json({ error: 'User not found.' });
        }

        const ChannelMessageModel = getChannelModel(channel);
        const newMessage = new ChannelMessageModel({
            channel,
            username: user.username,
            profileImage: user.profileImage,
            message: message || null,
            image: image || null,
        });

        await newMessage.save();
        res.status(201).json({ message: 'Message sent successfully.' });
    } catch (err) {
        console.error('Error sending message:', err);
        res.status(500).json({ error: 'Failed to send message.' });
    }
});

function getLeaderboardModel(game) {
    switch (game) {
        case 'morpRouge':
            return MorpRougeLeaderboard;
        case 'morphou':
            return MorphouLeaderboard;
        case 'evilMorp':
            return EvilMorpLeaderboard;
        case 'sudoku':
            return SudokuLeaderboard;
        case 'slidingTile':
            return SlidingTileLeaderboard;
        default:
            throw new Error('Invalid game selected.');
    }
}

app.post('/leaderboard/submit', async (req, res) => {
    if (!req.session || !req.session.username) {
        return res.status(401).json({ error: 'You must be logged in to submit a score.' });
    }

    const { game, score, proof } = req.body;

    if (!game || !score || !proof) {
        return res.status(400).json({ error: 'Game, score, and proof (Base64 image) are required.' });
    }

    try {
        const user = await Accounts.findOne({ username: req.session.username });

        if (!user) {
            return res.status(404).json({ error: 'User not found.' });
        }

        const LeaderboardModel = getLeaderboardModel(game);

        const newEntry = new LeaderboardModel({
            username: user.username,
            score: parseInt(score, 10),
            proof,
        });

        await newEntry.save();

        res.status(201).json({ message: 'Score submitted successfully.' });
    } catch (err) {
        console.error('Error submitting score:', err);
        res.status(500).json({ error: 'Failed to submit score.' });
    }
});


app.get('/leaderboard/all', async (req, res) => {
    try {
        const morpRouge = await MorpRougeLeaderboard.find().sort({ score: -1 }).limit(5);
        const morphou = await MorphouLeaderboard.find().sort({ score: -1 }).limit(5);
        const evilMorp = await EvilMorpLeaderboard.find().sort({ score: -1 }).limit(5);
        const sudoku = await SudokuLeaderboard.find().sort({ score: -1 }).limit(5);
        const slidingTile = await SlidingTileLeaderboard.find().sort({ score: -1 }).limit(5);

        res.json({
            morpRouge,
            morphou,
            evilMorp,
            sudoku,
            slidingTile,
        });
    } catch (err) {
        console.error('Error fetching leaderboards:', err);
        res.status(500).json({ error: 'Failed to fetch leaderboards.' });
    }
});












// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server is running on port ${port}. :: http://localhost:${port}/`);
});

