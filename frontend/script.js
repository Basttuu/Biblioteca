const API_URL = window.location.origin;
let token = "";
let currentUser = null;
let editingBookId = null;
let editingUserId = null;

document.addEventListener("DOMContentLoaded", () => {
  // botones y enlaces
  document.getElementById("login-btn").addEventListener("click", login);
  document.getElementById("register-btn").addEventListener("click", register);
  document.getElementById("show-register").addEventListener("click", e => { e.preventDefault(); showRegister(); });
  document.getElementById("show-login").addEventListener("click", e => { e.preventDefault(); showLogin(); });
  document.getElementById("catalog-btn").addEventListener("click", () => showSection("catalog"));
  document.getElementById("mybooks-btn").addEventListener("click", () => showSection("mybooks"));
  document.getElementById("addbook-btn").addEventListener("click", () => toggleAddBook(true));
  document.getElementById("users-btn").addEventListener("click", () => { showSection("users"); loadUsers(); });
  document.getElementById("logout-btn").addEventListener("click", logout);
  document.getElementById("save-book-btn").addEventListener("click", addBook);
  document.getElementById("close-addbook").addEventListener("click", () => toggleAddBook(false));
  document.getElementById("close-edituser").addEventListener("click", () => toggleEditUser(false));
  document.getElementById("save-user-btn").addEventListener("click", saveEditedUser);

  showLogin();
});

function showSection(name){
  document.getElementById("catalog-section").classList.toggle("hidden", name !== "catalog");
  document.getElementById("mybooks-section").classList.toggle("hidden", name !== "mybooks");
  document.getElementById("users-section").classList.toggle("hidden", name !== "users");
}

function showRegister() {
  document.getElementById("login-section").classList.add("hidden");
  document.getElementById("register-section").classList.remove("hidden");
}

function showLogin() {
  document.getElementById("register-section").classList.add("hidden");
  document.getElementById("login-section").classList.remove("hidden");
}

function toggleAddBook(show){
  const modal = document.getElementById("addbook-modal");
  modal.classList.toggle("hidden", !show);
  if(!show){
    document.getElementById("book-title").value = "";
    document.getElementById("book-author").value = "";
    document.getElementById("book-genre").value = "";
    document.getElementById("book-review").value = "";
    editingBookId = null;
    document.getElementById("save-book-btn").onclick = addBook;
  }
}

function toggleEditUser(show){
  const modal = document.getElementById("edituser-modal");
  modal.classList.toggle("hidden", !show);
  if(!show) editingUserId = null;
}

function showError(msg){ console.error(msg); alert(msg); }

async function register(){
  const username = document.getElementById("register-username").value.trim();
  const password = document.getElementById("register-password").value;
  if(!username||!password){ showError("Completa usuario y contraseña"); return; }
  try{
    const res = await fetch(`${API_URL}/users/register`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({username,password}) });
    if(res.ok){ alert("Usuario registrado. Inicia sesión."); showLogin(); } 
    else{ showError(await res.text()); }
  }catch(err){ showError(err.message); }
}

async function login(){
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;
  if(!username||!password){ showError("Completa usuario y contraseña"); return; }
  try{
    const res = await fetch(`${API_URL}/users/login`, {
      method:"POST",
      headers:{"Content-Type":"application/x-www-form-urlencoded"},
      body:`username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    });
    if(res.ok){
      const data = await res.json();
      token = data.access_token;
      await fetchCurrentUser();
      document.getElementById("nav-links").classList.remove("hidden");
      document.getElementById("logout-btn").classList.remove("hidden");
      document.getElementById("login-section").classList.add("hidden");
      document.getElementById("register-section").classList.add("hidden");
      showSection("catalog");
      loadBooks();
      loadMyLoans();
    } else showError(await res.text());
  } catch(err){ showError(err.message); }
}

async function fetchCurrentUser(){
  try{
    const res = await fetch(`${API_URL}/users/me`, { headers:{Authorization:`Bearer ${token}`} });
    if(!res.ok) throw new Error("No se pudo obtener usuario");
    currentUser = await res.json();
    if(currentUser.role==="admin"){
      document.getElementById("addbook-btn").classList.remove("hidden");
      document.getElementById("users-btn").classList.remove("hidden");
      document.getElementById("mybooks-btn").classList.add("hidden");
    } else {
      document.getElementById("addbook-btn").classList.add("hidden");
      document.getElementById("users-btn").classList.add("hidden");
      document.getElementById("mybooks-btn").classList.remove("hidden");
    }
  } catch(err){ showError(err.message); }
}

async function loadBooks(){
  try{
    const res = await fetch(`${API_URL}/books/`, { headers: token?{Authorization:`Bearer ${token}`}:{} });
    if(!res.ok) throw new Error("Error cargando libros");
    const books = await res.json();
    const grid = document.getElementById("books-list");
    grid.innerHTML = "";
    books.forEach(b=>{
      const card = document.createElement("div");
      card.className="book-card card";
      let buttons = "";
      if(currentUser?.role!=="admin" && b.available) buttons+=`<button class="btn" onclick="borrowBook(${b.id})">Pedir prestado</button>`;
      if(currentUser?.role==="admin"){
        buttons+=`<button class="btn secondary" onclick="editBook(${b.id})">Editar</button>`;
        buttons+=`<button class="btn danger" onclick="deleteBook(${b.id})">Eliminar</button>`;
      }
      buttons+=`<button class="btn secondary" onclick="recommendBooks(${b.id})">Ver similares</button>`;
      card.innerHTML = `
        <h4>${escapeHtml(b.title)}</h4>
        <p><em>${escapeHtml(b.author)}</em></p>
        <p>Disponibilidad: <strong>${b.available?"Disponible":"Prestado"}</strong></p>
        <div style="margin-top:8px;">${buttons}</div>
        <div id="rec-${b.id}" class="recommendations"></div>
      `;
      grid.appendChild(card);
    });
  } catch(err){ showError(err.message); }
}

async function addBook(){
  const title=document.getElementById("book-title").value.trim();
  const author=document.getElementById("book-author").value.trim();
  const genre=document.getElementById("book-genre").value.trim();
  const review=document.getElementById("book-review").value.trim();
  if(!title||!author){ showError("Título y autor son obligatorios"); return; }
  try{
    const res = await fetch(`${API_URL}/books/`, {
      method:"POST",
      headers:{ "Content-Type":"application/json", Authorization:`Bearer ${token}` },
      body:JSON.stringify({title,author,genre,review})
    });
    if(res.ok){ toggleAddBook(false); loadBooks(); alert("Libro agregado"); }
    else showError(await res.text());
  } catch(err){ showError(err.message); }
}

async function editBook(bookId){
  const booksRes = await fetch(`${API_URL}/books/`);
  const books = await booksRes.json();
  const book = books.find(b=>b.id===bookId);
  if(!book) return showError("Libro no encontrado");
  document.getElementById("book-title").value=book.title;
  document.getElementById("book-author").value=book.author;
  document.getElementById("book-genre").value=book.genre;
  document.getElementById("book-review").value=book.review;
  editingBookId=bookId;
  toggleAddBook(true);
  document.getElementById("save-book-btn").onclick=saveEditedBook;
}

async function saveEditedBook(){
  if(editingBookId===null) return;
  const title=document.getElementById("book-title").value.trim();
  const author=document.getElementById("book-author").value.trim();
  const genre=document.getElementById("book-genre").value.trim();
  const review=document.getElementById("book-review").value.trim();
  if(!title||!author){ showError("Título y autor son obligatorios"); return; }
  try{
    const res=await fetch(`${API_URL}/books/${editingBookId}`, {
      method:"PUT",
      headers:{ "Content-Type":"application/json", Authorization:`Bearer ${token}` },
      body:JSON.stringify({title,author,genre,review})
    });
    if(res.ok){ toggleAddBook(false); loadBooks(); alert("Libro actualizado"); editingBookId=null; }
    else showError(await res.text());
  } catch(err){ showError(err.message); }
}

async function deleteBook(bookId){
  if(!confirm("¿Eliminar libro?")) return;
  try{
    const res=await fetch(`${API_URL}/books/${bookId}`, { method:"DELETE", headers:{ Authorization:`Bearer ${token}` } });
    if(res.ok){ loadBooks(); alert("Libro eliminado"); } 
    else showError(await res.text());
  } catch(err){ showError(err.message); }
}

async function borrowBook(bookId){
  if(currentUser.role==="admin"){ showError("Los administradores no pueden pedir libros prestados"); return; }
  try{
    const res = await fetch(`${API_URL}/loans/borrow/${bookId}`, { method:"POST", headers:{Authorization:`Bearer ${token}`} });
    if(res.ok){ alert("Libro prestado"); loadBooks(); loadMyLoans(); } 
    else showError(await res.text());
  } catch(err){ showError(err.message); }
}

async function loadMyLoans(){
  if(!currentUser) return;
  try{
    const res = await fetch(`${API_URL}/loans/my`, { headers:{Authorization:`Bearer ${token}`} });
    if(!res.ok) throw new Error("Error cargando préstamos");
    const loans = await res.json();
    const container = document.getElementById("mybooks-list");
    container.innerHTML="";
    if(loans.length===0){ container.innerHTML="<p>No tienes préstamos</p>"; return; }
    for(const loan of loans){
      const booksRes=await fetch(`${API_URL}/books/`);
      const books = await booksRes.json();
      const book = books.find(b=>b.id===loan.book_id) || {title:"Desconocido"};
      const returned = loan.returned_at!==null;
      const div=document.createElement("div");
      div.className="loan-entry card";
      div.innerHTML = `
        <p><strong>${escapeHtml(book.title)}</strong> - Prestado el: ${new Date(loan.borrowed_at).toLocaleString()}</p>
        <p>Estado: ${returned?"Devuelto":"En préstamo"}</p>
        ${!returned?`<button class="btn" onclick="returnLoan(${loan.id})">Devolver</button>`:""}
      `;
      container.appendChild(div);
    }
  } catch(err){ showError(err.message); }
}

async function returnLoan(loanId){
  try{
    const res = await fetch(`${API_URL}/loans/return/${loanId}`, { method:"POST", headers:{Authorization:`Bearer ${token}`} });
    if(res.ok){ alert("Libro devuelto"); loadBooks(); loadMyLoans(); } 
    else showError(await res.text());
  } catch(err){ showError(err.message); }
}

function logout(){
  token=""; currentUser=null;
  document.getElementById("nav-links").classList.add("hidden");
  document.getElementById("login-section").classList.remove("hidden");
  document.getElementById("catalog-section").classList.add("hidden");
  document.getElementById("mybooks-section").classList.add("hidden");
  document.getElementById("users-section").classList.add("hidden");
  toggleAddBook(false);
}

function escapeHtml(s){ if(!s) return ""; return s.replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m])); }

async function recommendBooks(bookId){
  const container=document.getElementById(`rec-${bookId}`);
  if(!container) return;
  if(container.innerHTML.trim()!==""){ container.innerHTML=""; return; }
  try{
    const res=await fetch(`${API_URL}/recommend/${bookId}`);
    if(!res.ok) throw new Error("Error obteniendo recomendaciones");
    let recs=await res.json();
    recs = recs.filter((r,i,self)=> i===self.findIndex(t=>t.title===r.title && t.author===r.author));
    if(recs.length===0){ container.innerHTML="<p>No hay recomendaciones</p>"; return; }
    container.innerHTML="<h5>📌 Libros recomendados:</h5>";
    recs.forEach(r=>{
      const div=document.createElement("div");
      div.className="rec-card";
      div.innerHTML=`<p><strong>${escapeHtml(r.title)}</strong> - ${escapeHtml(r.author)} (${r.genre})</p>`;
      container.appendChild(div);
    });
  } catch(err){ alert(err.message); }
}

/*================== USUARIOS ==================*/
async function loadUsers(){
  if(currentUser.role!=="admin") return;
  try{
    const res = await fetch(`${API_URL}/users/`, { headers:{Authorization:`Bearer ${token}`} });
    if(!res.ok) throw new Error("Error cargando usuarios");
    const users = await res.json();
    const container=document.getElementById("users-list");
    container.innerHTML="";
    users.forEach(u=>{
      const div=document.createElement("div");
      div.className="user-entry card";
      div.innerHTML=`
        <p><strong>${escapeHtml(u.username)}</strong> - Rol: ${u.role}</p>
        <button class="btn secondary" onclick="editUser(${u.id})">Editar</button>
        <button class="btn danger" onclick="deleteUser(${u.id})">Eliminar</button>
      `;
      container.appendChild(div);
    });
  } catch(err){ showError(err.message); }
}

function editUser(userId){
  editingUserId=userId;
  toggleEditUser(true);
  fetch(`${API_URL}/users/${userId}`, { headers:{Authorization:`Bearer ${token}`} })
    .then(res=>res.json())
    .then(u=>{
      document.getElementById("edit-username").value=u.username;
      document.getElementById("edit-role").value=u.role;
    })
    .catch(err=>showError(err.message));
}

async function saveEditedUser(){
  if(editingUserId===null) return;
  const username=document.getElementById("edit-username").value.trim();
  const role=document.getElementById("edit-role").value;
  if(!username){ showError("El usuario no puede estar vacío"); return; }
  try{
    const res=await fetch(`${API_URL}/users/${editingUserId}`, {
      method:"PUT",
      headers:{ "Content-Type":"application/json", Authorization:`Bearer ${token}` },
      body:JSON.stringify({username,role})
    });
    if(res.ok){ toggleEditUser(false); loadUsers(); alert("Usuario actualizado"); }
    else showError(await res.text());
  } catch(err){ showError(err.message); }
}

async function deleteUser(userId){
  if(!confirm("¿Estás seguro de eliminar este usuario?")) return;
  try{
    const res=await fetch(`${API_URL}/users/${userId}`, { method:"DELETE", headers:{Authorization:`Bearer ${token}`} });
    if(res.ok){ loadUsers(); alert("Usuario eliminado"); } 
    else showError(await res.text());
  } catch(err){ showError(err.message); }
}

// Abrir modal para editar usuario
async function editUser(userId) {
  editingUserId = userId;
  const user = (await fetch(`${API_URL}/users/`)).json()
    .then(users => users.find(u => u.id === userId));
  
  if (!user) return showError("Usuario no encontrado");

  // Rellenar modal con datos existentes
  document.getElementById("edit-username").value = user.username;
  document.getElementById("edit-role").value = user.role;

  document.getElementById("edituser-modal").classList.remove("hidden");

  // Asignar función al botón guardar
  document.getElementById("save-user-btn").onclick = saveEditedUser;
}

// Guardar cambios de usuario
async function saveEditedUser() {
  if (!editingUserId) return showError("No hay usuario seleccionado");

  const username = document.getElementById("edit-username").value.trim();
  const role = document.getElementById("edit-role").value;

  if (!username) return showError("El nombre de usuario no puede estar vacío");

  try {
    const res = await fetch(`${API_URL}/users/${editingUserId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ username, role }) // Aquí envías lo que tu backend acepte
    });

    if (!res.ok) {
      const txt = await res.text();
      return showError("Error actualizando usuario: " + txt);
    }

    const updatedUser = await res.json();
    alert(`Usuario actualizado: ${updatedUser.username || "rol cambiado"}`);
    document.getElementById("edituser-modal").classList.add("hidden");
    loadUsers(); // recargar lista de usuarios
    editingUserId = null;

  } catch (err) {
    showError("Error en fetch: " + err.message);
  }
}

// Cerrar modal
document.getElementById("close-edituser").addEventListener("click", () => {
  document.getElementById("edituser-modal").classList.add("hidden");
  editingUserId = null;
});

