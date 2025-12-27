/*
 * Directory Operations Demo
 */

#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

#define TEST_DIR "/tmp/gem5_testdir"

int main() {
    printf("gem5 Directory Operations Demo\n");
    printf("================================\n\n");
    
    // Create directory
    printf("=== Creating directory ===\n");
    if (mkdir(TEST_DIR, 0755) == 0) {
        printf("Directory created: %s\n", TEST_DIR);
    } else if (errno == EEXIST) {
        printf("Directory already exists: %s\n", TEST_DIR);
    } else {
        perror("mkdir");
        return 1;
    }
    
    // Create nested directory
    char nested[256];
    snprintf(nested, sizeof(nested), "%s/subdir", TEST_DIR);
    if (mkdir(nested, 0755) == 0) {
        printf("Nested directory created: %s\n", nested);
    }
    
    // Create some files
    printf("\n=== Creating files ===\n");
    const char *files[] = {"file1.txt", "file2.txt", "file3.txt"};
    
    for (int i = 0; i < 3; i++) {
        char path[256];
        snprintf(path, sizeof(path), "%s/%s", TEST_DIR, files[i]);
        
        int fd = open(path, O_CREAT | O_WRONLY, 0644);
        if (fd >= 0) {
            char content[64];
            snprintf(content, sizeof(content), "Content of %s\n", files[i]);
            write(fd, content, strlen(content));
            close(fd);
            printf("Created: %s\n", path);
        }
    }
    
    // List directory contents
    printf("\n=== Directory contents ===\n");
    DIR *dir = opendir(TEST_DIR);
    if (dir) {
        struct dirent *entry;
        int count = 0;
        
        while ((entry = readdir(dir)) != NULL) {
            // Skip . and ..
            if (strcmp(entry->d_name, ".") == 0 || 
                strcmp(entry->d_name, "..") == 0)
                continue;
            
            printf("  [%d] %s (inode: %ld)\n", 
                   ++count, entry->d_name, entry->d_ino);
        }
        
        closedir(dir);
        printf("Total entries: %d\n", count);
    } else {
        perror("opendir");
    }
    
    // Get directory stats
    printf("\n=== Directory statistics ===\n");
    struct stat st;
    if (stat(TEST_DIR, &st) == 0) {
        printf("Directory: %s\n", TEST_DIR);
        printf("  Mode: 0%o\n", st.st_mode & 0777);
        printf("  Links: %ld\n", st.st_nlink);
        printf("  Size: %ld\n", st.st_size);
    }
    
    // Change to directory
    printf("\n=== Changing directory ===\n");
    char cwd[256];
    getcwd(cwd, sizeof(cwd));
    printf("Current directory: %s\n", cwd);
    
    if (chdir(TEST_DIR) == 0) {
        getcwd(cwd, sizeof(cwd));
        printf("Changed to: %s\n", cwd);
        
        // List current directory
        dir = opendir(".");
        if (dir) {
            printf("Contents of current directory:\n");
            struct dirent *entry;
            while ((entry = readdir(dir)) != NULL) {
                if (strcmp(entry->d_name, ".") != 0 && 
                    strcmp(entry->d_name, "..") != 0)
                    printf("  %s\n", entry->d_name);
            }
            closedir(dir);
        }
        
        // Change back
        chdir("..");
    }
    
    // Clean up
    printf("\n=== Cleaning up ===\n");
    
    // Delete files
    for (int i = 0; i < 3; i++) {
        char path[256];
        snprintf(path, sizeof(path), "%s/%s", TEST_DIR, files[i]);
        if (unlink(path) == 0) {
            printf("Deleted: %s\n", path);
        }
    }
    
    // Delete nested directory
    if (rmdir(nested) == 0) {
        printf("Deleted: %s\n", nested);
    }
    
    // Delete main directory
    if (rmdir(TEST_DIR) == 0) {
        printf("Deleted: %s\n", TEST_DIR);
    }
    
    printf("\nDemo complete!\n");
    return 0;
}
