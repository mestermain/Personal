// Personal Portfolio JavaScript System
// Features: Theme Switcher (Red/Light), Top Reading Progress Indicator, Floating Back-to-Top Button, Card Spotlight Glow, Skill Animations, AJAX Contact Form, Admin Mobile Sidebar Drawer

document.addEventListener('DOMContentLoaded', () => {

    // -------------------------------------------------------------
    // 1. Single Light Theme Enforcement
    // -------------------------------------------------------------
    document.documentElement.setAttribute('data-theme', 'light');
    localStorage.setItem('theme', 'light');

    // -------------------------------------------------------------
    // 2. Admin Sidebar Drawer Toggle for Mobile (<992px)
    // -------------------------------------------------------------
    const adminSidebarToggle = document.getElementById('admin-sidebar-toggle');
    const adminSidebar = document.querySelector('.admin-sidebar');
    if (adminSidebarToggle && adminSidebar) {
        let overlay = document.querySelector('.admin-sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'admin-sidebar-overlay';
            document.body.appendChild(overlay);
        }

        function toggleAdminSidebar() {
            adminSidebar.classList.toggle('sidebar-open');
            overlay.classList.toggle('show');
        }

        adminSidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleAdminSidebar();
        });

        overlay.addEventListener('click', () => {
            adminSidebar.classList.remove('sidebar-open');
            overlay.classList.remove('show');
        });
    }

    // -------------------------------------------------------------
    // 3. Top Reading Progress Indicator & Floating Back-to-Top Button
    // -------------------------------------------------------------
    const progressBar = document.getElementById('scroll-progress-bar');
    const backToTopBtn = document.getElementById('back-to-top-btn');

    window.addEventListener('scroll', () => {
        const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (totalHeight > 0) {
            const progress = (window.scrollY / totalHeight) * 100;
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
        }

        if (backToTopBtn) {
            if (window.scrollY > 300) {
                backToTopBtn.classList.remove('opacity-0', 'pointer-events-none');
                backToTopBtn.classList.add('opacity-100', 'pointer-events-auto');
            } else {
                backToTopBtn.classList.remove('opacity-100', 'pointer-events-auto');
                backToTopBtn.classList.add('opacity-0', 'pointer-events-none');
            }
        }
    });

    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // -------------------------------------------------------------
    // 4. Card Spotlight Glow Hover Effect
    // -------------------------------------------------------------
    const cards = document.querySelectorAll('.card-editorial');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });

    // -------------------------------------------------------------
    // 5. Animated Skill Progress Bars (Intersection Observer)
    // -------------------------------------------------------------
    const skillFills = document.querySelectorAll('.skill-progress-fill');
    if (skillFills.length > 0 && 'IntersectionObserver' in window) {
        const skillObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const fill = entry.target;
                    const targetWidth = fill.getAttribute('data-progress') || '85%';
                    fill.style.width = targetWidth;
                    observer.unobserve(fill);
                }
            });
        }, { threshold: 0.2 });

        skillFills.forEach(fill => skillObserver.observe(fill));
    } else {
        skillFills.forEach(fill => {
            fill.style.width = fill.getAttribute('data-progress') || '85%';
        });
    }

    // -------------------------------------------------------------
    // 6. Mobile Navigation Drawer Toggle
    // -------------------------------------------------------------
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuIcon = document.getElementById('mobile-menu-icon');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isExpanded = mobileMenuBtn.getAttribute('aria-expanded') === 'true';
            
            mobileMenuBtn.setAttribute('aria-expanded', !isExpanded);
            mobileMenu.classList.toggle('hidden');

            if (mobileMenuIcon) {
                if (!isExpanded) {
                    mobileMenuIcon.classList.remove('fa-bars');
                    mobileMenuIcon.classList.add('fa-xmark');
                } else {
                    mobileMenuIcon.classList.remove('fa-xmark');
                    mobileMenuIcon.classList.add('fa-bars');
                }
            }
        });

        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                mobileMenuBtn.setAttribute('aria-expanded', 'false');
                if (mobileMenuIcon) {
                    mobileMenuIcon.classList.remove('fa-xmark');
                    mobileMenuIcon.classList.add('fa-bars');
                }
            });
        });

        document.addEventListener('click', (e) => {
            if (!mobileMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                if (!mobileMenu.classList.contains('hidden')) {
                    mobileMenu.classList.add('hidden');
                    mobileMenuBtn.setAttribute('aria-expanded', 'false');
                    if (mobileMenuIcon) {
                        mobileMenuIcon.classList.remove('fa-xmark');
                        mobileMenuIcon.classList.add('fa-bars');
                    }
                }
            }
        });
    }

    // -------------------------------------------------------------
    // 7. Portfolio Category Filtering
    // -------------------------------------------------------------
    const filterBtns = document.querySelectorAll('.portfolio-filter-btn');
    const projectCards = document.querySelectorAll('.project-item');

    if (filterBtns.length > 0 && projectCards.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => {
                    b.classList.remove('btn-theme-primary');
                    b.classList.add('btn-theme-outline');
                });

                btn.classList.remove('btn-theme-outline');
                btn.classList.add('btn-theme-primary');

                const filterValue = btn.getAttribute('data-filter');

                projectCards.forEach(card => {
                    const category = card.getAttribute('data-category');
                    if (filterValue === 'all' || category === filterValue) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }

    // -------------------------------------------------------------
    // 8. Contact Form AJAX Submission
    // -------------------------------------------------------------
    const contactForm = document.getElementById('contact-form');
    const contactStatus = document.getElementById('contact-status');

    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalBtnHtml = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>SENDING...`;

            const formData = new FormData(contactForm);

            try {
                const response = await fetch(contactForm.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                let data;
                try {
                    data = await response.json();
                } catch (parseErr) {
                    data = { status: 'error', message: `Server HTTP ${response.status} Error. Please verify database connection.` };
                }

                if (response.ok && data.status === 'success') {
                    contactStatus.innerHTML = `
                        <div class="alert alert-success bg-emerald-50 text-emerald-900 border border-emerald-300 rounded-lg p-4 mb-4 font-semibold text-sm flex items-center gap-2">
                            <i class="fas fa-check-circle text-emerald-600 text-base"></i> ${data.message}
                        </div>
                    `;
                    contactForm.reset();
                } else {
                    contactStatus.innerHTML = `
                        <div class="alert alert-danger bg-rose-50 text-rose-900 border border-rose-300 rounded-lg p-4 mb-4 font-semibold text-sm flex items-center gap-2">
                            <i class="fas fa-exclamation-triangle text-[#C62828] text-base"></i> ${data.message || 'Something went wrong.'}
                        </div>
                    `;
                }
            } catch (err) {
                contactStatus.innerHTML = `
                    <div class="alert alert-danger bg-rose-50 text-rose-900 border border-rose-300 rounded-lg p-4 mb-4 font-semibold text-sm flex items-center gap-2">
                        <i class="fas fa-exclamation-triangle text-[#C62828] text-base"></i> Unable to connect to server. Please try again.
                    </div>
                `;
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnHtml;
            }
        });
    }

    // -------------------------------------------------------------
    // 9. Instant Table Search Helper for Admin Tables
    // -------------------------------------------------------------
    function initTableSearch(inputId, tableId) {
        const searchInput = document.getElementById(inputId);
        const table = document.getElementById(tableId);
        if (searchInput && table) {
            const rows = table.querySelectorAll('tbody tr');
            searchInput.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase().trim();
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    if (!term || text.includes(term)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        }
    }

    initTableSearch('projectSearchInput', 'projectsTable');
    initTableSearch('skillSearchInput', 'skillsTable');
    initTableSearch('messageSearchInput', 'messagesTable');

    // -------------------------------------------------------------
    // 10. Smooth Scrolling Anchor Links
    // -------------------------------------------------------------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});
