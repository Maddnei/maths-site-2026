// Mobile Menu
document.addEventListener('DOMContentLoaded', () => {
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }
});

// Teacher Login Modal
function openLoginModal() {
    const modal = document.getElementById('loginModal');
    const box = document.getElementById('loginModalBox');
    if (!modal || !box) return;
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.classList.remove('opacity-0');
        box.classList.remove('scale-95');
    }, 10);
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    const box = document.getElementById('loginModalBox');
    if (!modal || !box) return;
    modal.classList.add('opacity-0');
    box.classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 200);
}

// Global Image Lightbox
function openLightbox(imageUrl, caption) {
    const lightbox = document.getElementById('imageLightbox');
    const img = document.getElementById('lightboxImage');
    const cap = document.getElementById('lightboxCaption');
    const downloadBtn = document.getElementById('lightboxDownloadBtn');
    
    if (!lightbox || !img) return;
    
    img.src = imageUrl;
    if (cap) cap.textContent = caption || '';
    if (downloadBtn) downloadBtn.href = imageUrl;

    lightbox.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    const lightbox = document.getElementById('imageLightbox');
    if (!lightbox) return;
    lightbox.classList.add('hidden');
    document.body.style.overflow = '';
}

// Close lightbox on Escape key or background click
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeLightbox();
        closeLoginModal();
        closeStudentSubmitModal();
        closeAddResourceModal();
        closeAddAnnouncementModal();
        closeAddChapterModal();
        closeEditChapterModal();
    }
});

const imageLightboxEl = document.getElementById('imageLightbox');
if (imageLightboxEl) {
    imageLightboxEl.addEventListener('click', (e) => {
        if (e.target === imageLightboxEl || e.target.id === 'lightboxImage') {
            closeLightbox();
        }
    });
}

// Student Submission Modal
function openStudentSubmitModal() {
    const modal = document.getElementById('studentSubmitModal');
    const box = document.getElementById('studentModalBox');
    if (!modal || !box) return;
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.classList.remove('opacity-0');
        box.classList.remove('scale-95');
    }, 10);
}

function closeStudentSubmitModal() {
    const modal = document.getElementById('studentSubmitModal');
    const box = document.getElementById('studentModalBox');
    if (!modal || !box) return;
    modal.classList.add('opacity-0');
    box.classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 200);
}

// Teacher Add Resource Modal
function openAddResourceModal() {
    const modal = document.getElementById('addResourceModal');
    const box = document.getElementById('resourceModalBox');
    if (!modal || !box) return;
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.classList.remove('opacity-0');
        box.classList.remove('scale-95');
    }, 10);
}

function closeAddResourceModal() {
    const modal = document.getElementById('addResourceModal');
    const box = document.getElementById('resourceModalBox');
    if (!modal || !box) return;
    modal.classList.add('opacity-0');
    box.classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 200);
}

// Teacher Add Announcement Modal
function openAddAnnouncementModal(defaultClassId) {
    const modal = document.getElementById('addAnnouncementModal');
    const box = document.getElementById('announcementModalBox');
    if (!modal || !box) return;
    
    const select = modal.querySelector('select[name="class_id"]');
    if (select && defaultClassId) {
        select.value = defaultClassId;
    }
    
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.classList.remove('opacity-0');
        box.classList.remove('scale-95');
    }, 10);
}

function closeAddAnnouncementModal() {
    const modal = document.getElementById('addAnnouncementModal');
    const box = document.getElementById('announcementModalBox');
    if (!modal || !box) return;
    modal.classList.add('opacity-0');
    box.classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 200);
}

// Teacher Add Chapter Modal
function openAddChapterModal() {
    const modal = document.getElementById('addChapterModal');
    const box = document.getElementById('chapterModalBox');
    if (!modal || !box) return;
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.classList.remove('opacity-0');
        box.classList.remove('scale-95');
    }, 10);
}

function closeAddChapterModal() {
    const modal = document.getElementById('addChapterModal');
    const box = document.getElementById('chapterModalBox');
    if (!modal || !box) return;
    modal.classList.add('opacity-0');
    box.classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 200);
}

// Teacher Edit Chapter Modal
function openEditChapterModal() {
    const modal = document.getElementById('editChapterModal');
    const box = document.getElementById('editChapterBox');
    if (!modal || !box) return;
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.classList.remove('opacity-0');
        box.classList.remove('scale-95');
    }, 10);
}

function closeEditChapterModal() {
    const modal = document.getElementById('editChapterModal');
    const box = document.getElementById('editChapterBox');
    if (!modal || !box) return;
    modal.classList.add('opacity-0');
    box.classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 200);
}
