const express = require("express");
const multer = require("multer");
const fs = require("fs");
const path = require("path");

const app = express();

const PORT = 3000;

/*
 * Folder where screenshots will be stored.
 *
 * __dirname = current directory
 */

const captureDirectory = path.join(__dirname, "captures");

/*
 * Create captures folder if it
 * doesn't already exist.
 */

if (!fs.existsSync(captureDirectory)) {
  fs.mkdirSync(captureDirectory, {
    recursive: true,
  });
}

/*
 * Multer configuration
 */

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, captureDirectory);
  },

  filename: (req, file, cb) => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");

    cb(null, `screen-${timestamp}.jpg`);
  },
});

const upload = multer({
  storage,
});

/*
 * Serve index.html
 */

app.use(express.static(__dirname));

/*
 * Receive screenshot
 */

app.post("/save-screenshot", upload.single("image"), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: "No image received",
      });
    }

    console.log("Screenshot saved:", req.file.path);

    res.json({
      success: true,
      filename: req.file.filename,
    });
  } catch (error) {
    console.error(error);

    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);

  console.log(`Screenshots directory: ${captureDirectory}`);
});





// {
//   session_id: "",
//   question_id :"",
//   blur_count:"",
//   answer_length:"0",
//   question_timing:"question_opened",
//   event : {
//     type : "",
//     key : ""
//   },
//   timestamps:""
// }
// {
//   session_id: "",
//   question_id :"",
//   blur_count:"",
//   answer_length:"0",
//   question_timing:"question_opened",
//   event : {
//     type : "",
//     key : ""
//   },
//   timestamps:""
// }
// {
//   session_id: "",
//   question_id :"",
//   blur_count:"",
//   answer_length:"1",
//   question_timing:"typing_started",
//   event : {
//     type : "keydown",
//     key : "k"
//   },
//   timestamps:""
// }
// {
//   session_id: "",
//   question_id :"",
//   blur_count:"",
//   answer_length:"1",
//   question_timing:"typing_started",
//   event : {
//     type : "keyup",
//     key : "k"
//   },
//   timestamps:""
// }
// {
//   session_id: "",
//   question_id :"",
//   blur_count:"1",
//   answer_length:"1",
//   question_timing:"typing_stopped",
//   event : {
//     type : "",
//     key : ""
//   },
//   timestamps:""
// }
// {
//   session_id: "",
//   question_id :"",
//   blur_count:"1",
//   answer_length:"1",
//   question_timing:"question_closed",
//   event : {
//     type : "",
//     key : ""
//   },
//   timestamps:""
// }