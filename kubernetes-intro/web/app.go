package main

import (
	"github.com/gorilla/mux"
	log "github.com/sirupsen/logrus"
	"net/http"
	"os"
	"path/filepath"
)
type App struct {
	StaticPath string
	Index string
}
func main() {
	r := mux.NewRouter()
	app := App{StaticPath: "/app", Index: "index.html"}
	r.Path("/health").Handler(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("ok"))
	})).Methods("GET")
	r.Path("/live").Handler(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("ok"))
	})).Methods("GET")
	r.Path("/hostname").Handler(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		h, err := os.Hostname()
		if err != nil {
			w.Write([]byte(err.Error()))
		}
		w.Write([]byte(h))
	})).Methods("GET")
	r.Path("/version").Handler(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		version := os.Getenv("VERSION")
		if version == "" {
			version = "latest"
		}
		w.Write([]byte(version))
	})).Methods("GET")
	r.PathPrefix("/").Handler(app).Methods("GET")

	port := os.Getenv("APP_PORT")
	if port == "" {
		port = "8000"
	}
	server := http.Server{
		Addr: ":"+port,
		Handler: r,
	}

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("failed run server: %v", err)
	}
}

func (a App) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	path, err := filepath.Abs(r.URL.Path)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if path == "/" {
		http.ServeFile(w, r, filepath.Join(a.StaticPath, a.Index))
		return
	}

	path = filepath.Join(a.StaticPath, path)

	_, err = os.Stat(path)
	if os.IsNotExist(err) {
		http.ServeFile(w, r, filepath.Join(a.StaticPath, a.Index))
		return
	} else if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	http.FileServer(http.Dir(a.StaticPath)).ServeHTTP(w, r)
}
