#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

FILE *fptr;

long long generateAccountNumber() {
    return 1000000000LL + rand() % 9000000000LL;
}

void insertToFile(char *name, long long acc_no, int balance, int pin) {
    fptr = fopen("Records.txt", "a");
    if (fptr == NULL) {
        printf("Error opening file.\n");
        return;
    }
    fprintf(fptr, "Name: %sAccount Number: %lld\nPIN: %d\nBalance: %d\n\n", name, acc_no, pin, balance);
    fclose(fptr);
}

void NewAccount() {
    char name[100];
    int choice, balance, pin;

    while (getchar() != '\n');
    printf("Enter your name: ");
    fgets(name, sizeof(name), stdin);

    printf("Welcome, %s", name);
    printf("Choose account type:\n");
    printf("1. Savings\n2. Current\n3. Salary\n4. Demat\n");
    scanf("%d", &choice);

    switch (choice) {
        case 1: printf("Savings Account - 6%% interest\n"); break;
        case 2: printf("Current Account selected\n"); break;
        case 3: printf("Salary Account selected\n"); break;
        case 4: printf("Demat Account selected\n"); break;
        default: printf("Invalid choice\n"); return;
    }

    printf("Set a 4-digit PIN: ");
    scanf("%d", &pin);
    printf("Enter initial deposit amount: ");
    scanf("%d", &balance);

    long long acc_no = generateAccountNumber();
    insertToFile(name, acc_no, balance, pin);
    printf("Account created! Your account number is: %lld\n", acc_no);
}

int verifyPIN(long long acc_no, int entered_pin, char *name_out, int *balance_out) {
    long long file_acc;
    int file_pin, file_balance;
    char name[100];
    int match = 0;

    FILE *fptr = fopen("Records.txt", "r");
    if (fptr == NULL) return 0;

    while (fscanf(fptr, "Name: %[^\n]\nAccount Number: %lld\nPIN: %d\nBalance: %d\n\n", name, &file_acc, &file_pin, &file_balance) == 4) {
        if (file_acc == acc_no && file_pin == entered_pin) {
            if (name_out) strcpy(name_out, name);
            if (balance_out) *balance_out = file_balance;
            match = 1;
            break;
        }
    }

    fclose(fptr);
    return match;
}

void Deposit() {
    long long acc_no, file_acc;
    int dep, balance, pin, file_pin;
    char name[100];
    int found = 0;

    printf("Enter Account Number: ");
    scanf("%lld", &acc_no);
    printf("Enter PIN: ");
    scanf("%d", &pin);

    FILE *fread = fopen("Records.txt", "r");
    FILE *fwrite = fopen("Temp.txt", "w");

    if (fread == NULL || fwrite == NULL) {
        printf("File error.\n");
        return;
    }

    while (fscanf(fread, "Name: %[^\n]\nAccount Number: %lld\nPIN: %d\nBalance: %d\n\n", name, &file_acc, &file_pin, &balance) == 4) {
        if (file_acc == acc_no) {
            if (file_pin != pin) {
                printf("Incorrect PIN. Access denied.\n");
                fclose(fread);
                fclose(fwrite);
                remove("Temp.txt");
                return;
            }

            printf("Account found for %s\n", name);
            printf("Current Balance: ₹%d\n", balance);
            printf("Enter amount to deposit: ₹");
            scanf("%d", &dep);

            if (dep <= 0) {
                printf("Invalid deposit amount.\n");
            } else {
                balance += dep;
                printf("Deposit successful. New Balance: ₹%d\n", balance);
            }
            found = 1;
        }
        fprintf(fwrite, "Name: %s\nAccount Number: %lld\nPIN: %d\nBalance: %d\n\n", name, file_acc, file_pin, balance);
    }

    fclose(fread);
    fclose(fwrite);

    remove("Records.txt");
    rename("Temp.txt", "Records.txt");

    if (!found)
        printf("Account not found.\n");
}

void Withdraw() {
    long long acc_no, file_acc;
    int withdraw_amt, balance, pin, file_pin;
    char name[100];
    int found = 0;
    const int MIN_BALANCE = 1000;

    printf("Enter Account Number: ");
    scanf("%lld", &acc_no);
    printf("Enter PIN: ");
    scanf("%d", &pin);

    FILE *fread = fopen("Records.txt", "r");
    FILE *fwrite = fopen("Temp.txt", "w");

    if (fread == NULL || fwrite == NULL) {
        printf("Error accessing files.\n");
        return;
    }

    while (fscanf(fread, "Name: %[^\n]\nAccount Number: %lld\nPIN: %d\nBalance: %d\n\n", name, &file_acc, &file_pin, &balance) == 4) {
        if (file_acc == acc_no) {
            if (file_pin != pin) {
                printf("Incorrect PIN. Access denied.\n");
                fclose(fread);
                fclose(fwrite);
                remove("Temp.txt");
                return;
            }

            printf("Account found for %s\n", name);
            printf("Current Balance: ₹%d\n", balance);
            printf("Enter amount to withdraw: ₹");
            scanf("%d", &withdraw_amt);

            if (withdraw_amt <= 0) {
                printf("Invalid withdrawal amount.\n");
            } else if (balance - withdraw_amt < MIN_BALANCE) {
                printf("Withdrawal denied. Minimum balance of ₹%d must be maintained.\n", MIN_BALANCE);
            } else {
                balance -= withdraw_amt;
                printf("Withdrawal successful. New Balance: ₹%d\n", balance);
            }
            found = 1;
        }
        fprintf(fwrite, "Name: %s\nAccount Number: %lld\nPIN: %d\nBalance: %d\n\n", name, file_acc, file_pin, balance);
    }

    fclose(fread);
    fclose(fwrite);

    remove("Records.txt");
    rename("Temp.txt", "Records.txt");

    if (!found)
        printf("Account number not found.\n");
}

void CheckBalance() {
    long long acc_no;
    int pin, balance;
    char name[100];

    printf("Enter Account Number: ");
    scanf("%lld", &acc_no);
    printf("Enter PIN: ");
    scanf("%d", &pin);

    if (verifyPIN(acc_no, pin, name, &balance)) {
        printf("\n=====================================\n");
        printf("Account Holder : %s\n", name);
        printf("Account Number : %lld\n", acc_no);
        printf("Current Balance: ₹%d\n", balance);
        printf("=====================================\n");
    } else {
        printf("Incorrect PIN or account not found.\n");
    }
}

void Menu() {
    int option;
    printf("\n=== Welcome to Vice Bank ===\n");
    printf("1. Open New Account\n");
    printf("2. Deposit\n");
    printf("3. Withdraw\n");
    printf("4. Check Balance\n");
    printf("5. Exit\n");
    printf("Enter your choice: ");
    scanf("%d", &option);

    switch (option) {
        case 1: NewAccount(); break;
        case 2: Deposit(); break;
        case 3: Withdraw(); break;
        case 4: CheckBalance(); break;
        case 5: printf("Thank you for banking with us!\n"); exit(0);
        default: printf("Invalid choice. Try again.\n");
    }
}

int main() {
    srand(time(NULL));
    while (1) {
        Menu();
    }
    return 0;
}