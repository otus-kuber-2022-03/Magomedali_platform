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
	r.PathPrefix("/").Handler(app).Methods("GET")

	server := http.Server{
		Addr: ":8888",
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