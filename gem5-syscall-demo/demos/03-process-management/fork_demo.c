/*
 * Basic Fork Demonstration
 */

#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    printf("=== gem5 Fork Demo ===\n\n");
    
    printf("Parent process starting\n");
    printf("  PID: %d\n", getpid());
    printf("  PPID: %d\n\n", getppid());
    
    printf("Calling fork()...\n");
    pid_t pid = fork();
    
    if (pid < 0) {
        // Fork failed
        perror("fork");
        return EXIT_FAILURE;
        
    } else if (pid == 0) {
        // Child process
        printf("\n[CHILD] I'm the child process!\n");
        printf("[CHILD] My PID: %d\n", getpid());
        printf("[CHILD] My parent's PID: %d\n", getppid());
        printf("[CHILD] Doing some work...\n");
        
        // Simulate work
        for (int i = 0; i < 3; i++) {
            printf("[CHILD] Working... %d\n", i + 1);
        }
        
        printf("[CHILD] Exiting with status 42\n");
        return 42;
        
    } else {
        // Parent process
        printf("\n[PARENT] I'm the parent process!\n");
        printf("[PARENT] My PID: %d\n", getpid());
        printf("[PARENT] Created child with PID: %d\n", pid);
        printf("[PARENT] Waiting for child to finish...\n");
        
        int status;
        pid_t child_pid = wait(&status);
        
        if (WIFEXITED(status)) {
            int exit_status = WEXITSTATUS(status);
            printf("\n[PARENT] Child %d exited with status %d\n", 
                   child_pid, exit_status);
        }
        
        printf("[PARENT] All done!\n");
        return 0;
    }
}
