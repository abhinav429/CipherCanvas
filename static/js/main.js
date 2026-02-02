(function () {
  "use strict";

  const panelHide = document.getElementById("panel-hide");
  const panelReveal = document.getElementById("panel-reveal");
  const tabs = document.querySelectorAll(".tab");
  const formHide = document.getElementById("form-hide");
  const formReveal = document.getElementById("form-reveal");
  const hideStatus = document.getElementById("hide-status");
  const revealStatus = document.getElementById("reveal-status");
  const revealResult = document.getElementById("reveal-result");
  const revealMessage = document.getElementById("reveal-message");
  const btnHide = document.getElementById("btn-hide");
  const btnReveal = document.getElementById("btn-reveal");

  function switchTab(tabId) {
    tabs.forEach(function (t) {
      t.classList.toggle("active", t.getAttribute("data-tab") === tabId);
    });
    panelHide.classList.toggle("active", tabId === "hide");
    panelReveal.classList.toggle("active", tabId === "reveal");
    hideStatus.textContent = "";
    revealStatus.textContent = "";
    revealStatus.className = "status";
    revealResult.hidden = true;
  }

  tabs.forEach(function (t) {
    t.addEventListener("click", function () {
      switchTab(t.getAttribute("data-tab"));
    });
  });

  function setHideStatus(text, isError) {
    hideStatus.textContent = text;
    hideStatus.className = "status" + (isError ? " error" : " success");
  }

  function setRevealStatus(text, isError) {
    revealStatus.textContent = text;
    revealStatus.className = "status" + (isError ? " error" : " success");
  }

  formHide.addEventListener("submit", async function (e) {
    e.preventDefault();
    const imageInput = document.getElementById("hide-image");
    const messageInput = document.getElementById("hide-message");
    const passwordInput = document.getElementById("hide-password");

    if (!imageInput.files || !imageInput.files[0]) {
      setHideStatus("Please select an image.", true);
      return;
    }
    if (!messageInput.value.trim()) {
      setHideStatus("Please enter a message.", true);
      return;
    }
    if (!passwordInput.value) {
      setHideStatus("Please enter a password.", true);
      return;
    }

    btnHide.disabled = true;
    setHideStatus("Hiding message…");

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("message", messageInput.value.trim());
    formData.append("password", passwordInput.value);

    try {
      const res = await fetch("/api/hide", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json().catch(function () { return {}; });
        setHideStatus(data.error || "Something went wrong.", true);
        return;
      }

      const blob = await res.blob();
      const filename = res.headers.get("Content-Disposition")
        ? res.headers.get("Content-Disposition").split("filename=")[1]?.replace(/"/g, "").trim()
        : "ciphercanvas_stego.png";
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      setHideStatus("Done! Your stego-image has been downloaded.");
    } catch (err) {
      setHideStatus("Network error. Please try again.", true);
    } finally {
      btnHide.disabled = false;
    }
  });

  formReveal.addEventListener("submit", async function (e) {
    e.preventDefault();
    const imageInput = document.getElementById("reveal-image");
    const passwordInput = document.getElementById("reveal-password");

    if (!imageInput.files || !imageInput.files[0]) {
      setRevealStatus("Please select a stego-image.", true);
      return;
    }
    if (!passwordInput.value) {
      setRevealStatus("Please enter the password.", true);
      return;
    }

    btnReveal.disabled = true;
    setRevealStatus("Extracting message…");
    revealResult.hidden = true;

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("password", passwordInput.value);

    try {
      const res = await fetch("/api/reveal", {
        method: "POST",
        body: formData,
      });

      const data = await res.json().catch(function () { return {}; });

      if (!res.ok) {
        setRevealStatus(data.error || "Something went wrong.", true);
        return;
      }

      revealMessage.textContent = data.message || "";
      revealResult.hidden = false;
      setRevealStatus("Message extracted successfully.");
    } catch (err) {
      setRevealStatus("Network error. Please try again.", true);
    } finally {
      btnReveal.disabled = false;
    }
  });
})();
